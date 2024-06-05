using Microsoft.AspNetCore.Mvc;
using FetchNewsProject.Models;
using System.Collections.Generic;
using Microsoft.Extensions.Logging;
using FetchNewsProject.Data;
using System.Linq;

namespace FetchNewsProject.Controllers
{
    public class NewsViewController : Controller
    {
        private readonly NewsContext _context;
        private readonly ILogger<NewsViewController> _logger;

        public NewsViewController(ILogger<NewsViewController> logger, NewsContext context)
        {
            _logger = logger;
            _context = context;
        }

        public IActionResult Index(string source, string searchQueryInput, string fromDate, string toDate)
        {
            try
            {
                var query = _context.NewsItems.AsQueryable();
                
                if (query == null) 
                {
                    return NotFound();
                }

                if (!string.IsNullOrEmpty(source))
                {
                    query = query.Where(n => n.Source == source);
                }
                if (!string.IsNullOrEmpty(searchQueryInput))
                {
                    query = query.Where(n => n.Title.Contains(searchQueryInput) || n.Summary.Contains(searchQueryInput));
                }

                // Parse the fromDate and toDate
                if (DateTime.TryParse(fromDate, out DateTime parsedFromDate))
                {
                    query = query.Where(n => n.Date >= parsedFromDate);
                }
                if (DateTime.TryParse(toDate, out DateTime parsedToDate))
                {
                    query = query.Where(n => n.Date <= parsedToDate);
                }

                var newsItems = query.OrderByDescending(n => n.Date ?? DateTime.MinValue).ToList();
                var sources = _context.NewsItems.Select(n => n.Source).Distinct().ToList();
                var searchQuery = _context.NewsItems.Select(n => n.SearchQuery).Distinct().ToList();

                ViewBag.Sources = sources;
                ViewBag.CurrentSource = source;
                ViewBag.SearchWord = searchQueryInput;
                ViewBag.SearchQuery = searchQuery;

                return View(newsItems);
            }
            catch (Exception ex)
            {
                _logger.LogError(ex, "Failed to load news items.");
                return View("Error");
            }
        }
    }
}
