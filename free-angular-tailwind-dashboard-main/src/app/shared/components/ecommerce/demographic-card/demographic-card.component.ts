import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { DropdownComponent } from '../../ui/dropdown/dropdown.component';
import { DropdownItemComponent } from '../../ui/dropdown/dropdown-item/dropdown-item.component';
import { CountryMapComponent } from '../country-map/country-map.component';

@Component({
  selector: 'app-demographic-card',
  imports: [
    CommonModule,
    CountryMapComponent,
    DropdownComponent,
    DropdownItemComponent,
  ],
  templateUrl: './demographic-card.component.html',
})
export class DemographicCardComponent {
  isOpen = false;

  toggleDropdown() {
    this.isOpen = !this.isOpen;
  }

  closeDropdown() {
    this.isOpen = false;
  }

  countries = [
    {
      img: '/images/country/country-01.svg',
      alt: 'usa',
      name: 'USA',
      customers: '2,379 Customers',
      percent: 79,
    },
    {
      img: '/images/country/country-02.svg',
      alt: 'france',
      name: 'France',
      customers: '589 Customers',
      percent: 23,
    },
  ];
}
