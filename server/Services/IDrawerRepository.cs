using System.Collections.Generic;
using ToolSense.WebApp.Models;

namespace ToolSense.WebApp.Services
{
    public interface IDrawerRepository
    {
        IEnumerable<Drawer> GetAll();
        Drawer? GetByNumber(int number);
    }
}
