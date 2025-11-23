import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { InputFieldComponent } from '../../../form/input/input-field.component';
import { LabelComponent } from '../../../form/label/label.component';
import { ButtonComponent } from '../../../ui/button/button.component';
import { FormsModule } from '@angular/forms';


interface Product {
  name: string;
  price: number;
  quantity: number;
  discount: number;
  total: string;
}

interface FormData {
  name: string;
  price: number;
  quantity: number;
  discount: number;
}


@Component({
  selector: 'app-create-invoice-table',
  imports: [
    CommonModule,
    InputFieldComponent,
    LabelComponent,
    FormsModule,
  ],
  templateUrl: './create-invoice-table.component.html',
  styles: ``
})


export class CreateInvoiceTableComponent {

   products: Product[] = [
    { name: 'Macbook pro 13”', price: 1200, quantity: 1, discount: 0, total: (1200 * 1).toFixed(2) },
    { name: 'Apple Watch Ultra', price: 300, quantity: 1, discount: 50, total: (300 * 1 * 0.5).toFixed(2) },
    { name: 'iPhone 15 Pro Max', price: 800, quantity: 2, discount: 0, total: (800 * 2).toFixed(2) },
    { name: 'iPad Pro 3rd Gen', price: 900, quantity: 1, discount: 0, total: (900 * 1).toFixed(2) }
  ];

  form: FormData = {
    name: '',
    price: 0,
    quantity: 1,
    discount: 0
  };

  get subtotal(): number {
    return this.products.reduce((sum, p) => sum + Number(p.total), 0);
  }

  get vat(): number {
    return this.subtotal * 0.1;
  }

  get total(): number {
    return this.subtotal + this.vat;
  }

  handleDelete(index: number) {
    this.products = this.products.filter((_, i) => i !== index);
  }

  handleQuantityChange(delta: number) {
    this.form.quantity = Math.max(1, this.form.quantity + delta);
  }

  handleSubmit(event: Event) {
    event.preventDefault();
    if (this.form.name && this.form.price > 0) {
      const total = (
        this.form.price *
        this.form.quantity *
        (1 - this.form.discount / 100)
      ).toFixed(2);

      this.products = [...this.products, { ...this.form, total }];
      this.form = { name: '', price: 0, quantity: 1, discount: 0 };
    }
  }
}
