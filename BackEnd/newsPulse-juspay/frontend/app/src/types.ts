export interface Article {
  category: string;
  heading: string;
  source: string;
  date: string;
  summary: string;
  image_url?: string; // Added optional image_url field
}