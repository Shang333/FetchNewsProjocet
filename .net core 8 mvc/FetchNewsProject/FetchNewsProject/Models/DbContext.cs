using Microsoft.EntityFrameworkCore;
using FetchNewsProject.Models;

namespace FetchNewsProject.Data
{
    public class NewsContext : DbContext
    {
        public NewsContext(DbContextOptions<NewsContext> options) : base(options)
        {
        }

        public DbSet<NewsItem> NewsItems { get; set; }
    }
}
