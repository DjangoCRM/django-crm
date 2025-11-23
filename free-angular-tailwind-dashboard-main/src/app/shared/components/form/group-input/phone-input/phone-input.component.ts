import { CommonModule } from '@angular/common';
import { Component, Input, Output, EventEmitter, OnInit } from '@angular/core';

export interface CountryCode {
  code: string;
  label: string;
}

@Component({
  selector: 'app-phone-input',
  imports: [
    CommonModule,
  ],
  templateUrl: './phone-input.component.html',
  styles: ``
})
export class PhoneInputComponent {

  @Input() countries: CountryCode[] = [];
  @Input() placeholder: string = '+1 (555) 000-0000';
  @Input() selectPosition: 'start' | 'end' = 'start';
  @Output() phoneChange = new EventEmitter<string>();

  selectedCountry: string = '';
  phoneNumber: string = '';

  countryCodes: { [key: string]: string } = {};

  ngOnInit() {
    if (this.countries.length > 0) {
      this.selectedCountry = this.countries[0].code;
      this.countryCodes = this.countries.reduce(
        (acc, { code, label }) => ({ ...acc, [code]: label }),
        {}
      );
      this.phoneNumber = this.countryCodes[this.selectedCountry] || '';
    }
  }

  handleCountryChange(event: Event) {
    const newCountry = (event.target as HTMLSelectElement).value;
    this.selectedCountry = newCountry;
    this.phoneNumber = this.countryCodes[newCountry] || '';
    this.phoneChange.emit(this.phoneNumber);
  }

  handlePhoneNumberChange(event: Event) {
    const newPhoneNumber = (event.target as HTMLInputElement).value;
    this.phoneNumber = newPhoneNumber;
    this.phoneChange.emit(newPhoneNumber);
  }
}
