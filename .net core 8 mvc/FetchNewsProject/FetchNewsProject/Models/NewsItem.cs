using System;
using System.ComponentModel.DataAnnotations;

namespace FetchNewsProject.Models
{
    public class NewsItem
    {
        [Key]
        public int Id { get; set; }
        public string? Source { get; set; }
        public DateTime? Date { get; set; }
        [Display(Name = "Formatted Date")]
        public string? FormattedDate => Date?.ToString("yyyy-MM-dd");
        public string? Title { get; set; }
        public string? Summary { get; set; }
        public string? Link { get; set; }
        [Display(Name = "Image")]
        public string? ImageData { get; set; }
        public string? SearchQuery { get; set; }
    }
}
