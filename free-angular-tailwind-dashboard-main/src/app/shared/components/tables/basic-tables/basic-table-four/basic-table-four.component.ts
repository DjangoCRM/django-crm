import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { BadgeComponent } from '../../../ui/badge/badge.component';
import { TableDropdownComponent } from '../../../common/table-dropdown/table-dropdown.component';

@Component({
  selector: 'app-basic-table-four',
  imports: [
    CommonModule,
    BadgeComponent,
    TableDropdownComponent,
  ],
  templateUrl: './basic-table-four.component.html',
  styles: ``
})
export class BasicTableFourComponent {

  campaigns = [
    {
      id: 1,
      creator: {
        image: '/images/user/user-01.jpg',
        name: 'Wilson Gouse',
      },
      campaign: {
        image: '/images/brand/brand-01.svg',
        name: 'Grow your brand by...',
        type: 'Ads campaign',
      },
      status: 'Success',
    },
    {
      id: 2,
      creator: {
        image: '/images/user/user-02.jpg',
        name: 'Wilson Gouse',
      },
      campaign: {
        image: '/images/brand/brand-02.svg',
        name: 'Make Better Ideas...',
        type: 'Ads campaign',
      },
      status: 'Pending',
    },
    {
      id: 3,
      creator: {
        image: '/images/user/user-03.jpg',
        name: 'Wilson Gouse',
      },
      campaign: {
        image: '/images/brand/brand-03.svg',
        name: 'Increase your website tra...',
        type: 'Ads campaign',
      },
      status: 'Success',
    },
    {
      id: 4,
      creator: {
        image: '/images/user/user-04.jpg',
        name: 'Wilson Gouse',
      },
      campaign: {
        image: '/images/brand/brand-04.svg',
        name: 'Grow your brand by...',
        type: 'Ads campaign',
      },
      status: 'Failed',
    },
    {
      id: 5,
      creator: {
        image: '/images/user/user-05.jpg',
        name: 'Wilson Gouse',
      },
      campaign: {
        image: '/images/brand/brand-05.svg',
        name: 'Grow your brand by...',
        type: 'Ads campaign',
      },
      status: 'Success',
    },
    {
      id: 6,
      creator: {
        image: '/images/user/user-06.jpg',
        name: 'Wilson Gouse',
      },
      campaign: {
        image: '/images/brand/brand-06.svg',
        name: 'Grow your brand by...',
        type: 'Ads campaign',
      },
      status: 'Success',
    },
  ];

  handleViewMore() {
    console.log('View More clicked');
    // Add your view more logic here
  }

  handleDelete() {
    console.log('Delete clicked');
    // Add your delete logic here
  }
}
