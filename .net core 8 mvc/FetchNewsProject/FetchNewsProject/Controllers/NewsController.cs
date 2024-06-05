using Microsoft.AspNetCore.Http;
using Microsoft.AspNetCore.Mvc;
using System.Collections.Generic; // 如果要接收一個列表的數據
using FetchNewsProject.Models;
using FetchNewsProject.Data;

namespace FetchNewsProject.Controllers
{
    [Route("api/[controller]")]
    [ApiController]
    public class NewsController : ControllerBase
    {
        private readonly NewsContext _context;

        public NewsController(NewsContext context)
        {
            _context = context;
        }

        [HttpPost]
        public IActionResult Post([FromBody] List<NewsItem> newsItems)
        {
            if (newsItems == null || newsItems.Count == 0)
            {
                return BadRequest("No news items provided.");
            }

            _context.NewsItems.AddRange(newsItems);
            _context.SaveChanges();

            return Ok("Data saved to database successfully!");
        }
        [HttpDelete("clear")]
        public IActionResult ClearNewsItems()
        {
            try
            {
                // ToList() 確保查詢立即執行，這樣可以避免在操作中持有開啟的 DataReader
                var newsItems = _context.NewsItems.ToList();
                if (newsItems.Any())
                {
                    _context.NewsItems.RemoveRange(newsItems);
                    _context.SaveChanges();
                    return Ok("All news items have been deleted.");
                }
            }
            catch (Exception ex)
            {
                return StatusCode(500, "An error occurred while clearing news items.");
            }

            return NoContent(); // 當沒有內容需要刪除時返回
        }
    }
}
