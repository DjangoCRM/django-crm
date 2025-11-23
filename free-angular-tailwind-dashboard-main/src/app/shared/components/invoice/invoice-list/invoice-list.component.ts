import { CommonModule } from '@angular/common';
import { Component, ElementRef, HostListener } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { TableDropdownComponent } from '../../common/table-dropdown/table-dropdown.component';

interface Invoice {
  id: number;
  number: string;
  customer: string;
  creationDate: string;
  dueDate: string;
  total: number;
  status: "Paid" | "Unpaid" | "Draft";
}
interface SortState {
  sortBy: "number" | "customer" | "creationDate" | "dueDate" | "total";
  sortDirection: "asc" | "desc";
}

@Component({
  selector: 'app-invoice-list',
  imports: [
    CommonModule,
    FormsModule,
    TableDropdownComponent,
  ],
  templateUrl: './invoice-list.component.html',
  styles: ``
})
export class InvoiceListComponent {

  invoices: Invoice[] = [
    {
      id: 1,
      number: "#323534",
      customer: "Lindsey Curtis",
      creationDate: "August 7, 2028",
      dueDate: "February 28, 2028",
      total: 999,
      status: "Paid",
    },
    {
      id: 2,
      number: "#323535",
      customer: "John Doe",
      creationDate: "July 1, 2028",
      dueDate: "January 1, 2029",
      total: 1200,
      status: "Unpaid",
    },
    {
      id: 3,
      number: "#323536",
      customer: "Jane Smith",
      creationDate: "June 15, 2028",
      dueDate: "December 15, 2028",
      total: 850,
      status: "Draft",
    },
    {
      id: 4,
      number: "#323537",
      customer: "Michael Brown",
      creationDate: "May 10, 2028",
      dueDate: "November 10, 2028",
      total: 1500,
      status: "Paid",
    },
    {
      id: 5,
      number: "#323538",
      customer: "Emily Davis",
      creationDate: "April 5, 2028",
      dueDate: "October 5, 2028",
      total: 700,
      status: "Unpaid",
    },
    {
      id: 6,
      number: "#323539",
      customer: "Chris Wilson",
      creationDate: "March 1, 2028",
      dueDate: "September 1, 2028",
      total: 1100,
      status: "Paid",
    },
    {
      id: 7,
      number: "#323540",
      customer: "Jessica Lee",
      creationDate: "February 20, 2028",
      dueDate: "August 20, 2028",
      total: 950,
      status: "Draft",
    },
    {
      id: 8,
      number: "#323541",
      customer: "David Kim",
      creationDate: "January 15, 2028",
      dueDate: "July 15, 2028",
      total: 1300,
      status: "Paid",
    },
    {
      id: 9,
      number: "#323542",
      customer: "Sarah Clark",
      creationDate: "December 10, 2027",
      dueDate: "June 10, 2028",
      total: 800,
      status: "Unpaid",
    },
    {
      id: 10,
      number: "#323543",
      customer: "Matthew Lewis",
      creationDate: "November 5, 2027",
      dueDate: "May 5, 2028",
      total: 1400,
      status: "Paid",
    },
    {
      id: 11,
      number: "#323544",
      customer: "Olivia Walker",
      creationDate: "October 1, 2027",
      dueDate: "April 1, 2028",
      total: 1200,
      status: "Draft",
    },
    {
      id: 12,
      number: "#323545",
      customer: "Daniel Hall",
      creationDate: "September 20, 2027",
      dueDate: "March 20, 2028",
      total: 1000,
      status: "Paid",
    },
    {
      id: 13,
      number: "#323546",
      customer: "Sophia Allen",
      creationDate: "August 15, 2027",
      dueDate: "February 15, 2028",
      total: 900,
      status: "Unpaid",
    },
    {
      id: 14,
      number: "#323547",
      customer: "James Young",
      creationDate: "July 10, 2027",
      dueDate: "January 10, 2028",
      total: 1600,
      status: "Paid",
    },
    {
      id: 15,
      number: "#323548",
      customer: "Ava Hernandez",
      creationDate: "June 5, 2027",
      dueDate: "December 5, 2027",
      total: 1050,
      status: "Draft",
    },
    {
      id: 16,
      number: "#323549",
      customer: "William King",
      creationDate: "May 1, 2027",
      dueDate: "November 1, 2027",
      total: 1150,
      status: "Paid",
    },
    {
      id: 17,
      number: "#323550",
      customer: "Mia Wright",
      creationDate: "April 20, 2027",
      dueDate: "October 20, 2027",
      total: 980,
      status: "Unpaid",
    },
    {
      id: 18,
      number: "#323551",
      customer: "Benjamin Lopez",
      creationDate: "March 15, 2027",
      dueDate: "September 15, 2027",
      total: 1250,
      status: "Paid",
    },
    {
      id: 19,
      number: "#323552",
      customer: "Charlotte Hill",
      creationDate: "February 10, 2027",
      dueDate: "August 10, 2027",
      total: 890,
      status: "Draft",
    },
    {
      id: 20,
      number: "#323553",
      customer: "Elijah Scott",
      creationDate: "January 5, 2027",
      dueDate: "July 5, 2027",
      total: 1350,
      status: "Paid",
    },
    {
      id: 21,
      number: "#323554",
      customer: "Amelia Green",
      creationDate: "December 1, 2026",
      dueDate: "June 1, 2027",
      total: 1020,
      status: "Unpaid",
    },
    {
      id: 22,
      number: "#323555",
      customer: "Lucas Adams",
      creationDate: "November 20, 2026",
      dueDate: "May 20, 2027",
      total: 1120,
      status: "Paid",
    },
    {
      id: 23,
      number: "#323556",
      customer: "Harper Nelson",
      creationDate: "October 15, 2026",
      dueDate: "April 15, 2027",
      total: 970,
      status: "Draft",
    },
    {
      id: 24,
      number: "#323557",
      customer: "Henry Carter",
      creationDate: "September 10, 2026",
      dueDate: "March 10, 2027",
      total: 1280,
      status: "Paid",
    },
    {
      id: 25,
      number: "#323558",
      customer: "Evelyn Mitchell",
      creationDate: "August 5, 2026",
      dueDate: "February 5, 2027",
      total: 1080,
      status: "Unpaid",
    },
  ];


  selected: number[] = [];
  sort: SortState = { sortBy: 'number', sortDirection: 'asc' };
  currentPage: number = 1;
  filterStatus: 'All' | 'Unpaid' | 'Draft' | 'Paid' = 'All';
  search: string = '';
  showFilter: boolean = false;
  itemsPerPage: number = 10;

  constructor(private elementRef: ElementRef) {}

  @HostListener('document:click', ['$event'])
  handleClickOutside(event: MouseEvent) {
    const filterDropdown = this.elementRef.nativeElement.querySelector('.filter-dropdown');
    if (filterDropdown && !filterDropdown.contains(event.target as Node)) {
      this.showFilter = false;
    }
  }

  get filteredInvoices(): Invoice[] {
    return this.filterStatus === 'All'
      ? this.invoices
      : this.invoices.filter(invoice => invoice.status === this.filterStatus);
  }

  get searchedInvoices(): Invoice[] {
    return this.filteredInvoices.filter(
      invoice =>
        invoice.number.toLowerCase().includes(this.search.toLowerCase()) ||
        invoice.customer.toLowerCase().includes(this.search.toLowerCase())
    );
  }

  get sortedInvoices(): Invoice[] {
    return [...this.searchedInvoices].sort((a, b) => {
      let valA: string | number = a[this.sort.sortBy];
      let valB: string | number = b[this.sort.sortBy];
      if (this.sort.sortBy === 'total') {
        valA = Number(valA);
        valB = Number(valB);
      } else {
        valA = typeof valA === 'string' ? valA.toLowerCase() : valA;
        valB = typeof valB === 'string' ? valB.toLowerCase() : valB;
      }
      if (valA < valB) return this.sort.sortDirection === 'asc' ? -1 : 1;
      if (valA > valB) return this.sort.sortDirection === 'asc' ? 1 : -1;
      return 0;
    });
  }

  get paginatedInvoices(): Invoice[] {
    const start = (this.currentPage - 1) * this.itemsPerPage;
    return this.sortedInvoices.slice(start, start + this.itemsPerPage);
  }

  get totalPages(): number {
    return Math.ceil(this.sortedInvoices.length / this.itemsPerPage) || 1;
  }

  get startEntry(): number {
    return this.sortedInvoices.length === 0 ? 0 : (this.currentPage - 1) * this.itemsPerPage + 1;
  }

  get endEntry(): number {
    return Math.min(this.currentPage * this.itemsPerPage, this.sortedInvoices.length);
  }

  get visiblePages(): number[] {
    const maxVisible = 5;
    let start = Math.max(1, this.currentPage - Math.floor(maxVisible / 2));
    let end = Math.min(this.totalPages, start + maxVisible - 1);
    if (end - start + 1 < maxVisible) {
      start = Math.max(1, end - maxVisible + 1);
    }
    return Array.from({ length: end - start + 1 }, (_, i) => start + i);
  }

  get allPaginatedSelected(): boolean {
    return this.paginatedInvoices.length > 0 && this.paginatedInvoices.every(invoice => this.selected.includes(invoice.id));
  }

  ngOnInit(): void {}

  toggleSelectAll(): void {
    if (this.allPaginatedSelected) {
      this.selected = [];
    } else {
      this.selected = this.paginatedInvoices.map(i => i.id);
    }
  }

  toggleRow(id: number): void {
    this.selected = this.selected.includes(id)
      ? this.selected.filter(i => i !== id)
      : [...this.selected, id];
  }

  sortBy(field: 'number' | 'customer' | 'creationDate' | 'dueDate' | 'total'): void {
    this.sort = {
      sortBy: field,
      sortDirection: this.sort.sortBy === field && this.sort.sortDirection === 'asc' ? 'desc' : 'asc'
    };
    this.currentPage = 1;
  }

  goToPage(page: number): void {
    if (page >= 1 && page <= this.totalPages) {
      this.currentPage = page;
    }
  }

  nextPage(): void {
    if (this.currentPage < this.totalPages) {
      this.currentPage++;
    }
  }

  previousPage(): void {
    if (this.currentPage > 1) {
      this.currentPage--;
    }
  }

  setFilterStatus(status: 'All' | 'Unpaid' | 'Draft' | 'Paid'): void {
    this.filterStatus = status;
    this.currentPage = 1;
  }

  toggleFilter(): void {
    this.showFilter = !this.showFilter;
  }
}
