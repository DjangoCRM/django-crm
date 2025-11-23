import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { FaqItemOneComponent } from '../../../faqs/faq-item-one/faq-item-one.component';

@Component({
  selector: 'app-faqs-one',
  imports: [
    CommonModule,
    FaqItemOneComponent,
  ],
  templateUrl: './faqs-one.component.html',
  styles: ``
})
export class FaqsOneComponent {

  faqs = [
    {
      title: 'Do I get free updates?',
      content:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec quis magna ac nibh malesuada consectetur at vitae ipsum orem ipsum dolor sit amet, consectetur adipiscing elit nam fermentum, leo et lacinia accumsan.',
    },
    {
      title: 'Do I get free updates?',
      content:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec quis magna ac nibh malesuada consectetur at vitae ipsum orem ipsum dolor sit amet, consectetur adipiscing elit nam fermentum, leo et lacinia accumsan.',
    },
    {
      title: 'Can I Customize TailAdmin to suit my needs?',
      content:
        'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec quis magna ac nibh malesuada consectetur at vitae ipsum orem ipsum dolor sit amet, consectetur adipiscing elit nam fermentum, leo et lacinia accumsan.',
    },
    {
      title: 'What does Unlimited Projects mean?',
      content:
        'We have a 30-day refund policy. If you are not satisfied with the product, you can request a full refund within the first 30 days.',
    },
  ];

  openIndex: number | null = 0; // Initially open the first accordion

  toggleAccordion(index: number): void {
    this.openIndex = this.openIndex === index ? null : index; // Close if open, otherwise open the clicked one
  }
}
