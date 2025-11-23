import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';

@Component({
  selector: 'app-basic-table-five',
  imports: [
    CommonModule,
  ],
  templateUrl: './basic-table-five.component.html',
  styles: ``
})
export class BasicTableFiveComponent {

  tableData = [
    {
      id: 1,
      name: 'TailGrids',
      category: 'UI Kits',
      country: '/images/country/country-01.svg',
      cr: 'Dashboard',
      value: '12,499',
    },
    {
      id: 2,
      name: 'GrayGrids',
      category: 'Templates',
      country: '/images/country/country-02.svg',
      cr: 'Dashboard',
      value: '5498',
    },
    {
      id: 3,
      name: 'Uideck',
      category: 'Templates',
      country: '/images/country/country-03.svg',
      cr: 'Dashboard',
      value: '4621',
    },
    {
      id: 4,
      name: 'FormBold',
      category: 'SaaS',
      country: '/images/country/country-04.svg',
      cr: 'Dashboard',
      value: '13843',
    },
    {
      id: 5,
      name: 'NextAdmin',
      category: 'Templates',
      country: '/images/country/country-05.svg',
      cr: 'Dashboard',
      value: '7523',
    },
    {
      id: 6,
      name: 'Form Builder',
      category: 'Templates',
      country: '/images/country/country-06.svg',
      cr: 'Dashboard',
      value: '1,377',
    },
    {
      id: 7,
      name: 'AyroUI',
      category: 'Templates',
      country: '/images/country/country-07.svg',
      cr: 'Dashboard',
      value: '599,00',
    },
  ];

  handleFilter() {
    console.log('Filter clicked');
    // Add your filter logic here
  }

  handleSeeAll() {
    console.log('See all clicked');
    // Add your see all logic here
  }
}
