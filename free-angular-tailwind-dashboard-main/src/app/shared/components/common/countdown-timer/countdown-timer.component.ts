import { CommonModule } from '@angular/common';
import { Component, Input } from '@angular/core';

@Component({
  selector: 'app-countdown-timer',
  imports: [
    CommonModule,
  ],
  templateUrl: './countdown-timer.component.html',
  styles: ``
})
export class CountdownTimerComponent {

  @Input() targetDate!: Date;

  timeLeft = {
    days: 0,
    hours: 0,
    minutes: 0,
    seconds: 0,
  };

  private intervalId: any;

  ngOnInit(): void {
    this.startCountdown();
  }

  ngOnDestroy(): void {
    clearInterval(this.intervalId);
  }

  startCountdown(): void {
    this.intervalId = setInterval(() => {
      const now = new Date();
      const difference = this.targetDate.getTime() - now.getTime();

      if (difference > 0) {
        this.timeLeft.days = Math.floor(difference / (1000 * 60 * 60 * 24));
        this.timeLeft.hours = Math.floor((difference / (1000 * 60 * 60)) % 24);
        this.timeLeft.minutes = Math.floor((difference / (1000 * 60)) % 60);
        this.timeLeft.seconds = Math.floor((difference / 1000) % 60);
      } else {
        clearInterval(this.intervalId);
      }
    }, 1000);
  }

  formatTime(value: number): string {
    return value.toString().padStart(2, '0');
  }
}
