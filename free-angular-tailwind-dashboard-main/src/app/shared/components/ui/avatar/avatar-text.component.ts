import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-avatar-text',
  imports: [CommonModule],
  template: `<div
    class="flex h-10 w-10 items-center justify-center rounded-full 
    {{colorClass}} {{ className }}"
  >
    <span class="text-sm font-medium">{{ initials }}</span>
  </div>`,
})
export class AvatarTextComponent {
  @Input() name!: string;
  @Input() className = '';

  get initials(): string {
    if (!this.name) return '';
    return this.name
      .split(' ')
      .map((word) => word[0])
      .join('')
      .toUpperCase()
      .slice(0, 2);
  }

  get colorClass(): string {
    const colors = [
      'bg-brand-100 text-brand-600',
      'bg-pink-100 text-pink-600',
      'bg-cyan-100 text-cyan-600',
      'bg-orange-100 text-orange-600',
      'bg-green-100 text-green-600',
      'bg-purple-100 text-purple-600',
      'bg-yellow-100 text-yellow-600',
      'bg-error-100 text-error-600',
    ];
    const index = this.name
      .split('')
      .reduce((acc, char) => acc + char.charCodeAt(0), 0);
    return colors[index % colors.length];
  }
}
