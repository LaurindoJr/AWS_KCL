export interface Book {
  id: number;
  code: string;
  title: string;
  author: string;
  summary?: string;
  image_key?: string;
  thumb_url?: string | null;
  rentals?: Rental[];
}

export interface Rental {
  id: number;
  book_id: number;
  renter: string;
  start_date: string;
  end_date: string | null;
  status: 'OPEN' | 'CLOSED';
}

export interface BookFormData {
  code?: string;
  title: string;
  author: string;
  summary: string;
}
