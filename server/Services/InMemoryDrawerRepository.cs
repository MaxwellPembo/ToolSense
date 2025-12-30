using System;
using System.Collections.Generic;
using System.IO;
using System.Linq;
using System.Text;
using System.Timers;
using ToolSense.WebApp.Models;

namespace ToolSense.WebApp.Services
{
    public class InMemoryDrawerRepository : IDrawerRepository
    {
        private readonly List<Drawer> _drawers;
        private readonly object _lock = new object();
        private string? _csvPath;
        private FileSystemWatcher? _watcher;
        private System.Timers.Timer? _reloadTimer;

        public InMemoryDrawerRepository()
        {
            _drawers = new List<Drawer>();

            try
            {
                _csvPath = FindCsvPath("DrawerInfo.csv");
                if (!string.IsNullOrEmpty(_csvPath))
                {
                    LoadFromCsv(_csvPath);
                    // Setup a watcher to reload on file changes (debounced)
                    var dir = Path.GetDirectoryName(_csvPath) ?? Directory.GetCurrentDirectory();
                    var file = Path.GetFileName(_csvPath);

                    _reloadTimer = new System.Timers.Timer(500) { AutoReset = false };
                    _reloadTimer.Elapsed += (_, __) =>
                    {
                        try { LoadFromCsv(_csvPath); } catch { /* swallow */ }
                    };

                    _watcher = new FileSystemWatcher(dir, file)
                    {
                        NotifyFilter = NotifyFilters.LastWrite | NotifyFilters.FileName | NotifyFilters.Size
                    };

                    FileSystemEventHandler onChange = (_, __) =>
                    {
                        // restart debounce timer
                        try
                        {
                            if (_reloadTimer != null)
                            {
                                _reloadTimer.Stop();
                                _reloadTimer.Start();
                            }
                        }
                        catch { }
                    };

                    _watcher.Changed += onChange;
                    _watcher.Created += onChange;
                    _watcher.Renamed += (_, __) => onChange(_, __);
                    _watcher.EnableRaisingEvents = true;
                }
            }
            catch
            {
                // ignore and fall back to sample data
            }

            if (_drawers.Count == 0)
            {
                lock (_lock)
                {
                    _drawers.AddRange(new[]
                    {
                        // Status: true = available, false = taken
                        new Drawer { Number = 1, Tool = "Hammer", Status = true, IsOpen = true, CurrentUser = null, LastUser = "John Smith" },
                        new Drawer { Number = 2, Tool = "Screwdriver", Status = false, IsOpen = false, CurrentUser = "Jane Doe", LastUser = "John Smith" },
                        new Drawer { Number = 3, Tool = null, Status = false, IsOpen = false, CurrentUser = null, LastUser = null }
                    });
                }
            }
        }

        private static bool ParseBool(string s)
        {
            if (string.IsNullOrWhiteSpace(s)) return false;
            s = s.Trim();
            return s.Equals("true", System.StringComparison.OrdinalIgnoreCase) ||
                   s.Equals("yes", System.StringComparison.OrdinalIgnoreCase) ||
                   s.Equals("1");
        }

        private static string[] SplitCsvLine(string line)
        {
            // Very small CSV parser: handles simple commas and quoted fields
            var parts = new List<string>();
            var cur = new System.Text.StringBuilder();
            bool inQuotes = false;
            for (int i = 0; i < line.Length; i++)
            {
                var ch = line[i];
                if (ch == '"')
                {
                    if (inQuotes && i + 1 < line.Length && line[i + 1] == '"')
                    {
                        // escaped quote
                        cur.Append('"');
                        i++; // skip next
                    }
                    else
                    {
                        inQuotes = !inQuotes;
                    }
                }
                else if (ch == ',' && !inQuotes)
                {
                    parts.Add(cur.ToString());
                    cur.Clear();
                }
                else
                {
                    cur.Append(ch);
                }
            }
            parts.Add(cur.ToString());
            return parts.ToArray();
        }

        private static string? FindCsvPath(string fileName)
        {
            // Check a few likely locations: current directory, base directory and parents up to 6 levels
            var tryDirs = new List<string>
            {
                System.IO.Directory.GetCurrentDirectory(),
                System.AppContext.BaseDirectory
            };

            // add parent directories of AppContext.BaseDirectory up to 6 levels
            var dir = System.AppContext.BaseDirectory;
            for (int i = 0; i < 6; i++)
            {
                dir = System.IO.Path.GetFullPath(System.IO.Path.Combine(dir, ".."));
                tryDirs.Add(dir);
            }

            foreach (var d in tryDirs)
            {
                try
                {
                    var p = System.IO.Path.Combine(d, fileName);
                    if (System.IO.File.Exists(p)) return p;
                }
                catch { }
            }

            return null;
        }

        public IEnumerable<Drawer> GetAll()
        {
            return _drawers;
        }

        public Drawer? GetByNumber(int number)
        {
            return _drawers.FirstOrDefault(d => d.Number == number);
        }

        private void LoadFromCsv(string path)
        {
            // Read and parse file into a temporary list then swap under lock
            var lines = File.ReadAllLines(path)
                .Where(l => !string.IsNullOrWhiteSpace(l))
                .ToArray();

            var temp = new List<Drawer>();
            if (lines.Length > 1)
            {
                // Parse header to map column indexes (handles arbitrary order)
                var headerCols = SplitCsvLine(lines[0]).Select(h => h.Trim().ToLowerInvariant()).ToArray();

                int idxNumber = Array.FindIndex(headerCols, h => h.Contains("number"));
                int idxTool = Array.FindIndex(headerCols, h => h.Contains("tool"));
                int idxStatus = Array.FindIndex(headerCols, h => h.Contains("status"));
                int idxIsOpen = Array.FindIndex(headerCols, h => h.Contains("isopen") || h.Contains("is_open") || h.Contains("is open") || h.Contains("open"));
                int idxCurrentUser = Array.FindIndex(headerCols, h => h.Contains("currentuser") || h.Contains("current_user") || h.Contains("current user") || h.Contains("user"));
                int idxLastUser = Array.FindIndex(headerCols, h => h.Contains("lastuser") || h.Contains("last_user") || h.Contains("last user") || h.Contains("last"));

                // Fallback to conventional positions if some headers weren't recognized
                if (idxNumber < 0) idxNumber = 0;
                if (idxTool < 0) idxTool = 1;
                if (idxIsOpen < 0) idxIsOpen = 3;
                if (idxCurrentUser < 0) idxCurrentUser = 4;
                if (idxLastUser < 0) idxLastUser = 5;
                if (idxStatus < 0) idxStatus = 2; // assume status often near start

                for (int i = 1; i < lines.Length; i++)
                {
                    var cols = SplitCsvLine(lines[i]);

                    // helper to safely get and trim a column by index
                    string? GetCol(int idx)
                    {
                        if (idx < 0 || idx >= cols.Length) return null;
                        var v = cols[idx];
                        return v == null ? null : v.Trim();
                    }

                    var numCol = GetCol(idxNumber);
                    if (!int.TryParse(numCol ?? string.Empty, out var number)) continue;
                    var tool = string.IsNullOrWhiteSpace(GetCol(idxTool) ?? string.Empty) ? null : GetCol(idxTool);
                    var isOpen = ParseBool(GetCol(idxIsOpen) ?? string.Empty);
                    var currentUser = string.IsNullOrWhiteSpace(GetCol(idxCurrentUser) ?? string.Empty) ? null : GetCol(idxCurrentUser);
                    var lastUser = string.IsNullOrWhiteSpace(GetCol(idxLastUser) ?? string.Empty) ? null : GetCol(idxLastUser);

                    // Parse status column if present; otherwise derive from currentUser
                    bool statusBool;
                    var rawStatusCandidate = GetCol(idxStatus);
                    if (!string.IsNullOrWhiteSpace(rawStatusCandidate))
                    {
                        var rawStatus = rawStatusCandidate.Trim();
                        if (!bool.TryParse(rawStatus, out statusBool))
                        {
                            var r = rawStatus.ToLowerInvariant();
                            if (r == "1" || r == "yes" || r == "y") statusBool = true;
                            else if (r == "0" || r == "no" || r == "n") statusBool = false;
                            else if (r.Contains("tak")) statusBool = false;
                            else if (r.Contains("avail") || r.Contains("avalib")) statusBool = true;
                            else statusBool = string.IsNullOrWhiteSpace(currentUser) ? true : false;
                        }
                    }
                    else
                    {
                        statusBool = string.IsNullOrWhiteSpace(currentUser) ? true : false;
                    }

                    temp.Add(new Drawer
                    {
                        Number = number,
                        Tool = tool,
                        Status = statusBool,
                        IsOpen = isOpen,
                        CurrentUser = currentUser,
                        LastUser = lastUser
                    });
                }
            }

            if (temp.Count > 0)
            {
                lock (_lock)
                {
                    _drawers.Clear();
                    _drawers.AddRange(temp);
                }
            }
        }
    }
}
