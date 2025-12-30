namespace ToolSense.WebApp.Models
{
    public class Drawer
    {
        public int Number { get; set; }
        public string? Tool { get; set; }
        // `Status` is a boolean where `true` means Available and `false` means Taken
        public bool Status { get; set; }
        public bool IsOpen { get; set; }
        public string? CurrentUser { get; set; }
        public string? LastUser { get; set; }
    }
}
