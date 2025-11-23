import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';
import { FaqItemTwoComponent } from "../../../faqs/faq-item-two/faq-item-two.component";

@Component({
  selector: 'app-faqs-two',
  imports: [
    CommonModule,
    FaqItemTwoComponent
],
  templateUrl: './faqs-two.component.html',
  styles: ``
})
export class FaqsTwoComponent {

  accordionTwoData = [
    {
      title: 'Do I get free updates?',
      content: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec quis magna ac nibh malesuada consectetur at vitae ipsum orem ipsum dolor sit amet, consectetur adipiscing elit nam fermentum, leo et lacinia accumsan.'
    },
    {
      title: 'Which license type is suitable for me?',
      content: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec quis magna ac nibh malesuada consectetur at vitae ipsum orem ipsum dolor sit amet, consectetur adipiscing elit nam fermentum, leo et lacinia accumsan.'
    },
    {
      title: 'What are the Seats mentioned on pricing plans?',
      content: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec quis magna ac nibh malesuada consectetur at vitae ipsum orem ipsum dolor sit amet, consectetur adipiscing elit nam fermentum, leo et lacinia accumsan.'
    },
    {
      title: 'Can I Customize TailAdmin to suit my needs?',
      content: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec quis magna ac nibh malesuada consectetur at vitae ipsum orem ipsum dolor sit amet, consectetur adipiscing elit nam fermentum, leo et lacinia accumsan.'
    },
    {
      title: 'What does Unlimited Projects mean?',
      content: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec quis magna ac nibh malesuada consectetur at vitae ipsum orem ipsum dolor sit amet, consectetur adipiscing elit nam fermentum, leo et lacinia accumsan.'
    },
    {
      title: 'Can I upgrade to a higher plan?',
      content: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec quis magna ac nibh malesuada consectetur at vitae ipsum orem ipsum dolor sit amet, consectetur adipiscing elit nam fermentum, leo et lacinia accumsan.'
    },
    {
      title: 'Are there dark and light mode options?',
      content: 'Lorem ipsum dolor sit amet, consectetur adipiscing elit. Donec quis magna ac nibh malesuada consectetur at vitae ipsum orem ipsum dolor sit amet, consectetur adipiscing elit nam fermentum, leo et lacinia accumsan.'
    }
  ];

  openIndexFirstGroup: number | null = 0;
  openIndexSecondGroup: number | null = 0;

  get firstGroup() {
    return this.accordionTwoData.slice(0, 3);
  }

  get secondGroup() {
    return this.accordionTwoData.slice(3, 7);
  }

  toggleFirstGroup(index: number): void {
    console.log(index,'index')
    this.openIndexFirstGroup = this.openIndexFirstGroup === index ? null : index;
  }

  toggleSecondGroup(index: number): void {
    this.openIndexSecondGroup = this.openIndexSecondGroup === index ? null : index;
  }
}
