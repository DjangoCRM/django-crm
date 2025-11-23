import { Component } from '@angular/core';
import { ButtonComponent } from '../../../ui/button/button.component';

@Component({
  selector: 'app-billing-plan',
  imports: [
    ButtonComponent,
  ],
  templateUrl: './billing-plan.component.html',
  host:{
    class:'rounded-2xl border border-gray-200 bg-white xl:w-4/6 dark:border-gray-800 dark:bg-white/[0.03]'
  }
})
export class BillingPlanComponent {

}
