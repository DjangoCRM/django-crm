import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { BadgeComponent } from '../../../ui/badge/badge.component';

@Component({
  selector: 'app-basic-table-one',
  imports: [
    CommonModule,
    BadgeComponent,
  ],
  templateUrl: './basic-table-one.component.html',
  styles: ``
})
export class BasicTableOneComponent {

  tableData = [
    {
      id: 1,
      user: {
        image: '/images/user/user-17.jpg',
        name: 'Lindsey Curtis',
        role: 'Web Designer',
      },
      projectName: 'Agency Website',
      team: {
        images: [
          '/images/user/user-22.jpg',
          '/images/user/user-23.jpg',
          '/images/user/user-24.jpg',
        ],
      },
      budget: '3.9K',
      status: 'Active',
    },
    {
      id: 2,
      user: {
        image: '/images/user/user-18.jpg',
        name: 'Kaiya George',
        role: 'Project Manager',
      },
      projectName: 'Technology',
      team: {
        images: ['/images/user/user-25.jpg', '/images/user/user-26.jpg'],
      },
      budget: '24.9K',
      status: 'Pending',
    },
    {
      id: 3,
      user: {
        image: '/images/user/user-17.jpg',
        name: 'Zain Geidt',
        role: 'Content Writing',
      },
      projectName: 'Blog Writing',
      team: {
        images: ['/images/user/user-27.jpg'],
      },
      budget: '12.7K',
      status: 'Active',
    },
    {
      id: 4,
      user: {
        image: '/images/user/user-20.jpg',
        name: 'Abram Schleifer',
        role: 'Digital Marketer',
      },
      projectName: 'Social Media',
      team: {
        images: [
          '/images/user/user-28.jpg',
          '/images/user/user-29.jpg',
          '/images/user/user-30.jpg',
        ],
      },
      budget: '2.8K',
      status: 'Cancel',
    },
    {
      id: 5,
      user: {
        image: '/images/user/user-21.jpg',
        name: 'Carla George',
        role: 'Front-end Developer',
      },
      projectName: 'Website',
      team: {
        images: [
          '/images/user/user-31.jpg',
          '/images/user/user-32.jpg',
          '/images/user/user-33.jpg',
        ],
      },
      budget: '4.5K',
      status: 'Active',
    },
  ];

  getBadgeColor(status: string): 'success' | 'warning' | 'error' {
    if (status === 'Active') return 'success';
    if (status === 'Pending') return 'warning';
    return 'error';
  }
}
