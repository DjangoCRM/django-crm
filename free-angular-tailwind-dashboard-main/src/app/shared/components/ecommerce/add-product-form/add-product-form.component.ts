import { Component } from '@angular/core';
import { CommonModule } from '@angular/common';
import { LabelComponent } from '../../form/label/label.component';
import { InputFieldComponent } from '../../form/input/input-field.component';
import { SelectComponent } from '../../form/select/select.component';
import { TextAreaComponent } from '../../form/input/text-area.component';
import { ButtonComponent } from '../../ui/button/button.component';

@Component({
  selector: 'app-add-product-form',
  imports: [
    CommonModule,
    LabelComponent,
    InputFieldComponent,
    SelectComponent,
    TextAreaComponent,
    ButtonComponent
  ],
  templateUrl: './add-product-form.component.html',
  styles: ``
})
export class AddProductFormComponent {

  categories = [
    { value: 'Laptop', label: 'Laptop' },
    { value: 'Phone', label: 'Phone' },
    { value: 'Watch', label: 'Watch' },
    { value: 'Electronics', label: 'Electronics' },
    { value: 'Accessories', label: 'Accessories' }
  ];

  brands = [
    { value: '1', label: 'Apple' },
    { value: '2', label: 'Samsung' },
    { value: '3', label: 'LG' }
  ];

  availability = [
    { value: '1', label: 'In Stock' },
    { value: '2', label: 'Out of Stock' }
  ];

  colors = [
    { value: '1', label: 'Silver' },
    { value: '2', label: 'Black' },
    { value: '3', label: 'White' },
    { value: '4', label: 'Gray' }
  ];

  stockQuantity: number = 1;

  handleSelectChange(value: string) {
    console.log('Selected value:', value);
  }

  incrementQuantity() {
    this.stockQuantity++;
  }

  decrementQuantity() {
    if (this.stockQuantity > 0) {
      this.stockQuantity--;
    }
  }

  updateQuantity(value: string | number) {
    this.stockQuantity = typeof value === 'string' ? parseInt(value) || 0 : value;
  }

  onDraft() {
    console.log('Draft button clicked');
  }

  onPublish() {
    console.log('Publish Product button clicked');
  }
}
