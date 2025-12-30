using Microsoft.AspNetCore.Mvc;
using ToolSense.WebApp.Models;
using ToolSense.WebApp.Services;

namespace ToolSense.WebApp.Controllers;

[ApiController]
[Route("api/[controller]")]
public class DrawersController : ControllerBase
{
    private readonly IDrawerRepository _repository;

    public DrawersController(IDrawerRepository repository)
    {
        _repository = repository;
    }

    [HttpGet]
    public ActionResult<IEnumerable<Drawer>> Get()
    {
        var drawers = _repository.GetAll();
        return Ok(drawers);
    }

    [HttpGet("{number}")]
    public ActionResult<Drawer> Get(int number)
    {
        var drawer = _repository.GetByNumber(number);
        if (drawer == null) return NotFound();
        return Ok(drawer);
    }
}
