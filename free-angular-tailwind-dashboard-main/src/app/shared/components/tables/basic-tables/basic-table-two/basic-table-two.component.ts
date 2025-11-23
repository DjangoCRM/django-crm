import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { BadgeComponent } from '../../../ui/badge/badge.component';
import { AvatarTextComponent } from '../../../ui/avatar/avatar-text.component';
import { CheckboxComponent } from '../../../form/input/checkbox.component';

@Component({
  selector: 'app-basic-table-two',
  imports: [
    CommonModule,
    BadgeComponent,
    AvatarTextComponent,
    CheckboxComponent,
  ],
  templateUrl: './basic-table-two.component.html',
  styles: ``
})
export class BasicTableTwoComponent {

  tableRowData = [
    {
      id: 'DE124321',
      user: { initials: 'AB', name: 'John Doe', email: 'johndoe@gmail.com' },
      avatarColor: 'brand',
      product: { name: 'Software License', price: '$18,50.34', purchaseDate: '2024-06-15' },
      status: { type: 'Complete' },
      actions: { delete: true },
    },
    {
      id: 'DE124322',
      user: { initials: 'CD', name: 'Jane Smith', email: 'janesmith@gmail.com' },
      avatarColor: 'brand',
      product: { name: 'Cloud Hosting', price: '$12,99.00', purchaseDate: '2024-06-18' },
      status: { type: 'Pending' },
      actions: { delete: true },
    },
    {
      id: 'DE124323',
      user: { initials: 'EF', name: 'Michael Brown', email: 'michaelbrown@gmail.com' },
      avatarColor: 'brand',
      product: { name: 'Web Domain', price: '$9,50.00', purchaseDate: '2024-06-20' },
      status: { type: 'Cancel' },
      actions: { delete: true },
    },
    {
      id: 'DE124324',
      user: { initials: 'GH', name: 'Alice Johnson', email: 'alicejohnson@gmail.com' },
      avatarColor: 'brand',
      product: { name: 'SSL Certificate', price: '$2,30.45', purchaseDate: '2024-06-25' },
      status: { type: 'Pending' },
      actions: { delete: true },
    },
    {
      id: 'DE124325',
      user: { initials: 'IJ', name: 'Robert Lee', email: 'robertlee@gmail.com' },
      avatarColor: 'brand',
      product: { name: 'Premium Support', price: '$15,20.00', purchaseDate: '2024-06-30' },
      status: { type: 'Complete' },
      actions: { delete: true },
    },
  ];

  selectedRows: string[] = [];
  selectAll: boolean = false;

  handleSelectAll() {
    this.selectAll = !this.selectAll;
    if (this.selectAll) {
      this.selectedRows = this.tableRowData.map(row => row.id);
    } else {
      this.selectedRows = [];
    }
  }

  handleRowSelect(id: string) {
    if (this.selectedRows.includes(id)) {
      this.selectedRows = this.selectedRows.filter(rowId => rowId !== id);
    } else {
      this.selectedRows = [...this.selectedRows, id];
    }
  }

  getBadgeColor(type: string): 'success' | 'warning' | 'error' {
    if (type === 'Complete') return 'success';
    if (type === 'Pending') return 'warning';
    return 'error';
  }
}
