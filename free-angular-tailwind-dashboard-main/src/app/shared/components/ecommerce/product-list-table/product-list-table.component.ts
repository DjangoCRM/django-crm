import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { TableDropdownComponent } from '../../common/table-dropdown/table-dropdown.component';
import { ButtonComponent } from '../../ui/button/button.component';
import { RouterModule } from '@angular/router';

interface Product {
  id: number;
  name: string;
  image: string;
  category: string;
  brand: string;
  price: string;
  stock: string;
  createdAt: string;
}
interface Sort {
  key: keyof Product;
  asc: boolean;
}

@Component({
  selector: 'app-product-list-table',
  imports: [
    CommonModule,
    TableDropdownComponent,
    ButtonComponent,
    RouterModule,
  ],
  templateUrl: './product-list-table.component.html',
  styles: ``
})
export class ProductListTableComponent {

  products = [
    {
      id: 1,
      name: "Macbook pro M4",
      image: "/images/product/product-01.jpg",
      category: "Laptop",
      brand: "Apple",
      price: "$699",
      stock: "In Stock",
      createdAt: "12 Feb, 2027",
    },
    {
      id: 2,
      name: "Apple Watch Ultra",
      image: "/images/product/product-02.jpg",
      category: "Watch",
      brand: "Apple",
      price: "$1,579",
      stock: "Out of Stock",
      createdAt: "13 Mar, 2027",
    },
    {
      id: 3,
      name: "iPhone 15 Pro Max",
      image: "/images/product/product-03.jpg",
      category: "Phone",
      brand: "Apple",
      price: "$1,039",
      stock: "In Stock",
      createdAt: "19 Mar, 2027",
    },
    {
      id: 4,
      name: "iPad Pro 3rd Gen",
      image: "/images/product/product-04.jpg",
      category: "Electronics",
      brand: "Apple",
      price: "$43,999",
      stock: "In Stock",
      createdAt: "25 Apr, 2027",
    },
    {
      id: 5,
      name: "Samsung Galaxy S24 Ultra",
      image: "/images/product/product-05.jpg",
      category: "Phone",
      brand: "Samsung",
      price: "$699",
      stock: "In Stock",
      createdAt: "11 May, 2027",
    },
    {
      id: 6,
      name: "Airpods Pro 2nd Gen",
      image: "/images/product/product-01.jpg",
      category: "Accessories",
      brand: "Apple",
      price: "$839",
      stock: "In Stock",
      createdAt: "29 Jun, 2027",
    },
    {
      id: 7,
      name: "LG OLED & 4K Smart TV",
      image: "/images/product/product-02.jpg",
      category: "Electronics",
      brand: "LG",
      price: "$1,769",
      stock: "Out of Stock",
      createdAt: "22 Jul, 2027",
    },
    {
      id: 8,
      name: "Sony WH-1000XM5 Headphones",
      image: "/images/product/product-03.jpg",
      category: "Audio",
      brand: "Sony",
      price: "$399",
      stock: "In Stock",
      createdAt: "05 Aug, 2027",
    },
    {
      id: 9,
      name: "Dell XPS 13 Laptop",
      image: "/images/product/product-04.jpg",
      category: "Laptop",
      brand: "Dell",
      price: "$1,299",
      stock: "In Stock",
      createdAt: "18 Aug, 2027",
    },
    {
      id: 10,
      name: "Google Pixel 8 Pro",
      image: "/images/product/product-05.jpg",
      category: "Phone",
      brand: "Google",
      price: "$899",
      stock: "Out of Stock",
      createdAt: "02 Sep, 2027",
    },
    {
      id: 11,
      name: "Microsoft Surface Pro 9",
      image: "/images/product/product-02.jpg",
      category: "Tablet",
      brand: "Microsoft",
      price: "$1,099",
      stock: "In Stock",
      createdAt: "15 Sep, 2027",
    },
    {
      id: 12,
      name: "Canon EOS R5 Camera",
      image: "/images/product/product-03.jpg",
      category: "Camera",
      brand: "Canon",
      price: "$3,899",
      stock: "In Stock",
      createdAt: "28 Sep, 2027",
    },
    {
      id: 13,
      name: "Nintendo Switch OLED",
      image: "/images/product/product-04.jpg",
      category: "Gaming",
      brand: "Nintendo",
      price: "$349",
      stock: "Out of Stock",
      createdAt: "10 Oct, 2027",
    },
    {
      id: 14,
      name: "Razer DeathAdder V3 Mouse",
      image: "/images/product/product-05.jpg",
      category: "Accessories",
      brand: "Razer",
      price: "$89",
      stock: "In Stock",
      createdAt: "23 Oct, 2027",
    },
    {
      id: 15,
      name: "HP Envy 34 Monitor",
      image: "/images/product/product-01.jpg",
      category: "Monitor",
      brand: "HP",
      price: "$799",
      stock: "In Stock",
      createdAt: "05 Nov, 2027",
    },
    {
      id: 16,
      name: "Bose QuietComfort Earbuds",
      image: "/images/product/product-02.jpg",
      category: "Audio",
      brand: "Bose",
      price: "$279",
      stock: "In Stock",
      createdAt: "18 Nov, 2027",
    },
    {
      id: 17,
      name: "ASUS ROG Gaming Laptop",
      image: "/images/product/product-03.jpg",
      category: "Laptop",
      brand: "ASUS",
      price: "$2,199",
      stock: "Out of Stock",
      createdAt: "01 Dec, 2027",
    },
    {
      id: 18,
      name: "Logitech MX Master 3S",
      image: "/images/product/product-04.jpg",
      category: "Accessories",
      brand: "Logitech",
      price: "$119",
      stock: "In Stock",
      createdAt: "14 Dec, 2027",
    },
    {
      id: 19,
      name: "Steam Deck OLED",
      image: "/images/product/product-05.jpg",
      category: "Gaming",
      brand: "Valve",
      price: "$649",
      stock: "In Stock",
      createdAt: "27 Dec, 2027",
    },
    {
      id: 20,
      name: "Samsung 980 Pro SSD 2TB",
      image: "/images/product/product-01.jpg",
      category: "Storage",
      brand: "Samsung",
      price: "$299",
      stock: "In Stock",
      createdAt: "09 Jan, 2028",
    },
  ]

  selected: number[] = [];
  sort: Sort = { key: 'name', asc: true };
  page: number = 1;
  perPage: number = 7;
  showFilter: boolean = false;

  ngOnInit() {
    // Initialize component
  }

  sortedProducts(): Product[] {
    return [...this.products].sort((a, b) => {
      let valA: any = a[this.sort.key];
      let valB: any = b[this.sort.key];
      if (this.sort.key === 'price') {
        valA = parseFloat(valA.replace(/[^\d.]/g, ''));
        valB = parseFloat(valB.replace(/[^\d.]/g, ''));
      }
      if (valA < valB) return this.sort.asc ? -1 : 1;
      if (valA > valB) return this.sort.asc ? 1 : -1;
      return 0;
    });
  }

  paginatedProducts(): Product[] {
    const start = (this.page - 1) * this.perPage;
    return this.sortedProducts().slice(start, start + this.perPage);
  }

  totalPages(): number {
    return Math.ceil(this.products.length / this.perPage);
  }

  goToPage(n: number): void {
    if (n >= 1 && n <= this.totalPages()) {
      this.page = n;
    }
  }

  prevPage(): void {
    if (this.page > 1) {
      this.page--;
    }
  }

  nextPage(): void {
    if (this.page < this.totalPages()) {
      this.page++;
    }
  }

  toggleSelect(id: number): void {
    this.selected = this.selected.includes(id)
      ? this.selected.filter((i) => i !== id)
      : [...this.selected, id];
  }

  toggleAll(): void {
    const ids = this.paginatedProducts().map((p) => p.id);
    this.selected = this.isAllSelected()
      ? this.selected.filter((id) => !ids.includes(id))
      : [...new Set([...this.selected, ...ids])];
  }

  isAllSelected(): boolean {
    const ids = this.paginatedProducts().map((p) => p.id);
    return ids.length > 0 && ids.every((id) => this.selected.includes(id));
  }

  startItem(): number {
    return this.products.length === 0 ? 0 : (this.page - 1) * this.perPage + 1;
  }

  endItem(): number {
    return Math.min(this.page * this.perPage, this.products.length);
  }

  sortBy(key: keyof Product): void {
    this.sort = {
      key,
      asc: this.sort.key === key ? !this.sort.asc : true,
    };
  }

  toggleFilter(): void {
    this.showFilter = !this.showFilter;
  }

   handleViewMore() {
    console.log('View More clicked');
    // Add your view more logic here
  }

  handleDelete() {
    console.log('Delete clicked');
    // Add your delete logic here
  }
}
