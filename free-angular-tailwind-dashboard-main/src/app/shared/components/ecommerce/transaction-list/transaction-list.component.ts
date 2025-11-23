import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { RouterModule } from '@angular/router';
import { TableDropdownComponent } from '../../common/table-dropdown/table-dropdown.component';
import { FormsModule } from '@angular/forms';

interface Transaction {
  id: number;
  orderId: string;
  customer: string;
  email: string;
  amount: number;
  amountDisplay: string;
  status: 'Completed' | 'Pending' | 'Failed';
  dueDate: string;
}

interface SortState {
  key: 'customer' | 'email' | 'amount';
  asc: boolean;
}

@Component({
  selector: 'app-transaction-list',
  imports: [
    CommonModule,
    RouterModule,
    TableDropdownComponent,
    FormsModule,
  ],
  templateUrl: './transaction-list.component.html',
  styles: ``
})
export class TransactionListComponent {

   transactions: Transaction[] = [
    {
      id: 1,
      orderId: '#323534',
      customer: 'Lindsey Curtis',
      email: 'lindsey@example.com',
      amount: 699,
      amountDisplay: '$699',
      status: 'Completed',
      dueDate: '12 Feb, 2027',
    },
    {
      id: 2,
      orderId: '#323535',
      customer: 'Kaiya George',
      email: 'kaiya@example.com',
      amount: 1579,
      amountDisplay: '$1,579',
      status: 'Failed',
      dueDate: '13 Mar, 2027',
    },
    {
      id: 3,
      orderId: '#323536',
      customer: 'Zain Geidt',
      email: 'zain787@example.com',
      amount: 1039,
      amountDisplay: '$1,039',
      status: 'Pending',
      dueDate: '19 Mar, 2027',
    },
    {
      id: 4,
      orderId: '#323537',
      customer: 'Abram Schleifer',
      email: 'abram@example.com',
      amount: 43999,
      amountDisplay: '$43,999',
      status: 'Completed',
      dueDate: '25 Apr, 2027',
    },
    {
      id: 5,
      orderId: '#323538',
      customer: 'Carla George',
      email: 'carla65@example.com',
      amount: 919,
      amountDisplay: '$919',
      status: 'Completed',
      dueDate: '11 May, 2027',
    },
    {
      id: 6,
      orderId: '#323539',
      customer: 'Emery Culhane',
      email: 'emery09@example.com',
      amount: 839,
      amountDisplay: '$839',
      status: 'Completed',
      dueDate: '29 Jun, 2027',
    },
    {
      id: 7,
      orderId: '#323540',
      customer: 'Livia Donin',
      email: 'livia343@example.com',
      amount: 1769,
      amountDisplay: '$1,769',
      status: 'Failed',
      dueDate: '22 Jul, 2027',
    },
    {
      id: 8,
      orderId: '#323541',
      customer: 'Miracle Bator',
      email: 'miracle@example.com',
      amount: 7349,
      amountDisplay: '$7,349',
      status: 'Completed',
      dueDate: '05 Aug, 2027',
    },
    {
      id: 9,
      orderId: '#323542',
      customer: 'Lincoln Herwitz',
      email: 'lincoln@example.com',
      amount: 849,
      amountDisplay: '$849',
      status: 'Completed',
      dueDate: '09 Sep, 2027',
    },
    {
      id: 10,
      orderId: '#323543',
      customer: 'Ekstrom Bothman',
      email: 'ekstrom@example.com',
      amount: 679,
      amountDisplay: '$679',
      status: 'Completed',
      dueDate: '15 Nov, 2027',
    },
    {
      id: 11,
      orderId: '#323544',
      customer: 'Ava Smith',
      email: 'ava.smith@example.com',
      amount: 1200,
      amountDisplay: '$1,200',
      status: 'Pending',
      dueDate: '01 Dec, 2027',
    },
    {
      id: 12,
      orderId: '#323545',
      customer: 'Noah Lee',
      email: 'noah.lee@example.com',
      amount: 540,
      amountDisplay: '$540',
      status: 'Failed',
      dueDate: '15 Dec, 2027',
    },
    {
      id: 13,
      orderId: '#323546',
      customer: 'Mia Chen',
      email: 'mia.chen@example.com',
      amount: 3200,
      amountDisplay: '$3,200',
      status: 'Completed',
      dueDate: '22 Dec, 2027',
    },
    {
      id: 14,
      orderId: '#323547',
      customer: 'Ethan Patel',
      email: 'ethan.patel@example.com',
      amount: 2100,
      amountDisplay: '$2,100',
      status: 'Pending',
      dueDate: '05 Jan, 2028',
    },
    {
      id: 15,
      orderId: '#323548',
      customer: 'Sophia Kim',
      email: 'sophia.kim@example.com',
      amount: 980,
      amountDisplay: '$980',
      status: 'Completed',
      dueDate: '18 Jan, 2028',
    },
    {
      id: 16,
      orderId: '#323549',
      customer: 'Liam Brown',
      email: 'liam.brown@example.com',
      amount: 450,
      amountDisplay: '$450',
      status: 'Failed',
      dueDate: '28 Jan, 2028',
    },
    {
      id: 17,
      orderId: '#323550',
      customer: 'Olivia Wilson',
      email: 'olivia.wilson@example.com',
      amount: 1750,
      amountDisplay: '$1,750',
      status: 'Pending',
      dueDate: '10 Feb, 2028',
    },
    {
      id: 18,
      orderId: '#323551',
      customer: 'Mason Clark',
      email: 'mason.clark@example.com',
      amount: 600,
      amountDisplay: '$600',
      status: 'Completed',
      dueDate: '20 Feb, 2028',
    },
    {
      id: 19,
      orderId: '#323552',
      customer: 'Ella Davis',
      email: 'ella.davis@example.com',
      amount: 210,
      amountDisplay: '$210',
      status: 'Failed',
      dueDate: '01 Mar, 2028',
    },
    {
      id: 20,
      orderId: '#323553',
      customer: 'James Martinez',
      email: 'james.martinez@example.com',
      amount: 3300,
      amountDisplay: '$3,300',
      status: 'Completed',
      dueDate: '15 Mar, 2028',
    },
  ];

  selected: number[] = [];
  sort: SortState = { key: 'customer', asc: true };
  page: number = 1;
  search: string = '';
  filterDays: string = 'Last 7 Days';
  perPage: number = 10;

  get totalPages(): number {
    return Math.ceil(this.transactions.length / this.perPage) || 1;
  }

  get startEntry(): number {
    return this.transactions.length === 0 ? 0 : (this.page - 1) * this.perPage + 1;
  }

  get endEntry(): number {
    return Math.min(this.page * this.perPage, this.transactions.length);
  }

  get sortedRows(): Transaction[] {
    return [...this.transactions].sort((a, b) => {
      let valA = a[this.sort.key];
      let valB = b[this.sort.key];
      if (typeof valA === 'string') valA = valA.toLowerCase();
      if (typeof valB === 'string') valB = valB.toLowerCase();
      if (valA < valB) return this.sort.asc ? -1 : 1;
      if (valA > valB) return this.sort.asc ? 1 : -1;
      return 0;
    });
  }

  get filteredRows(): Transaction[] {
    return this.sortedRows.filter(
      (row) =>
        row.orderId.toLowerCase().includes(this.search.toLowerCase()) ||
        row.customer.toLowerCase().includes(this.search.toLowerCase()) ||
        row.email.toLowerCase().includes(this.search.toLowerCase())
    );
  }

  get paginatedRows(): Transaction[] {
    return this.filteredRows.slice(
      (this.page - 1) * this.perPage,
      this.page * this.perPage
    );
  }

  get totalPagesArray(): number[] {
    return Array.from({ length: this.totalPages }, (_, i) => i + 1);
  }

  toggleSelectAll(): void {
    if (this.selected.length === this.paginatedRows.length) {
      this.selected = [];
    } else {
      this.selected = this.paginatedRows.map((row) => row.id);
    }
  }

  isAllSelected(): boolean {
    return this.paginatedRows.every((row) => this.selected.includes(row.id));
  }

  toggleRow(id: number): void {
    if (this.selected.includes(id)) {
      this.selected = this.selected.filter((i) => i !== id);
    } else {
      this.selected = [...this.selected, id];
    }
  }

  sortBy(key: 'customer' | 'email' | 'amount'): void {
    this.sort = {
      key,
      asc: this.sort.key === key ? !this.sort.asc : true,
    };
    this.page = 1;
  }

  goToPage(n: number): void {
    if (n >= 1 && n <= this.totalPages) {
      this.page = n;
    }
  }

  onSearchChange(): void {
    this.page = 1; // Reset to first page on search
  }

  onFilterChange(): void {
    this.page = 1; // Reset to first page on filter change
  }

  handleViewMore(): void {
    // Logic for view more
  }

  handleDelete(): void {
    // Logic for delete
  }
}
