import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { ButtonComponent } from '../../../ui/button/button.component';

interface Invoice {
  id: number;
  name: string;
  date: string;
  price: string;
  plan: string;
  status: string;
}

@Component({
  selector: 'app-billing-invoice-table',
  imports: [
    CommonModule,
  ],
  templateUrl: './billing-invoice-table.component.html',
})
export class BillingInvoiceTableComponent {

  invoices: Invoice[] = [
    {
      id: 1,
      name: 'Invoice #012 - May 2024',
      date: 'May 01, 2024',
      price: '$120.00',
      plan: 'Starter Plan',
      status: 'Paid'
    },
    {
      id: 2,
      name: 'Invoice #013 - June 2024',
      date: 'June 01, 2024',
      price: '$120.00',
      plan: 'Starter Plan',
      status: 'Paid'
    },
    {
      id: 3,
      name: 'Invoice #014 - July 2024',
      date: 'July 01, 2024',
      price: '$120.00',
      plan: 'Starter Plan',
      status: 'Unpaid'
    },
    {
      id: 4,
      name: 'Invoice #015 - August 2024',
      date: 'August 01, 2024',
      price: '$250.00',
      plan: 'Pro Plan',
      status: 'Paid'
    },
    {
      id: 5,
      name: 'Invoice #016 - September 2024',
      date: 'September 01, 2024',
      price: '$250.00',
      plan: 'Pro Plan',
      status: 'Paid'
    },
    {
      id: 6,
      name: 'Invoice #017 - October 2024',
      date: 'October 01, 2024',
      price: '$250.00',
      plan: 'Pro Plan',
      status: 'Unpaid'
    },
    {
      id: 7,
      name: 'Invoice #018 - November 2024',
      date: 'November 01, 2024',
      price: '$500.00',
      plan: 'Enterprise Plan',
      status: 'Paid'
    },
    {
      id: 8,
      name: 'Invoice #019 - December 2024',
      date: 'December 01, 2024',
      price: '$500.00',
      plan: 'Enterprise Plan',
      status: 'Paid'
    },
    {
      id: 9,
      name: 'Invoice #020 - January 2025',
      date: 'January 01, 2025',
      price: '$500.00',
      plan: 'Enterprise Plan',
      status: 'Unpaid'
    },
    {
      id: 10,
      name: 'Invoice #021 - February 2025',
      date: 'February 01, 2025',
      price: '$500.00',
      plan: 'Enterprise Plan',
      status: 'Paid'
    },
    {
      id: 11,
      name: 'Invoice #022 - March 2025',
      date: 'March 01, 2025',
      price: '$120.00',
      plan: 'Starter Plan',
      status: 'Paid'
    },
    {
      id: 12,
      name: 'Invoice #023 - April 2025',
      date: 'April 01, 2025',
      price: '$120.00',
      plan: 'Starter Plan',
      status: 'Unpaid'
    }
  ];

  currentPage: number = 1;
  itemsPerPage: number = 5;

  get totalInvoices(): number {
    return this.invoices.length;
  }

  get totalPages(): number {
    return Math.ceil(this.totalInvoices / this.itemsPerPage);
  }

  get startItem(): number {
    return (this.currentPage - 1) * this.itemsPerPage + 1;
  }

  get endItem(): number {
    return Math.min(this.currentPage * this.itemsPerPage, this.totalInvoices);
  }

  get paginatedInvoices(): Invoice[] {
    return this.invoices.slice(
      (this.currentPage - 1) * this.itemsPerPage,
      this.currentPage * this.itemsPerPage
    );
  }

  visiblePages(): number[] {
    const maxVisible: number = 5;
    let start: number = Math.max(1, this.currentPage - Math.floor(maxVisible / 2));
    let end: number = Math.min(this.totalPages, start + maxVisible - 1);
    if (end - start + 1 < maxVisible) {
      start = Math.max(1, end - maxVisible + 1);
    }
    return Array.from({ length: end - start + 1 }, (_, i) => start + i);
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

  onDownloadAll(): void {
    console.log('Download All clicked');
  }

  onDownloadInvoice(id: number): void {
    console.log(`Download invoice ${id}`);
  }

  onViewInvoice(id: number): void {
    console.log(`View invoice ${id}`);
  }
}
