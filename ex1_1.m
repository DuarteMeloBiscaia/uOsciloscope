clear all; close all; clc;

f0 = 1000;
Q  = 10;
w0 = 2*pi*f0;

num = [w0/Q 0];
den = [1 w0/Q w0^2];

f = 0:1:8000;
w = 2*pi*f;

Ta = freqs(num, den, w);

Ga = 20*log10(abs(Ta));
phi = angle(Ta)*180/pi;

figure(1)
plot(f, Ga, 'linewidth', 2); grid on
xlabel('Frequency, Hz')
ylabel('Magnitude G_a(\omega) [dB]')
title('Analog band-pass filter')
axis([0 8000 -50 5])

figure(2)
plot(f, phi, 'linewidth', 2); grid on
xlabel('Frequency, Hz')
ylabel('Phase \phi_a(\omega) [deg]')
title('Phase of analog band-pass filter')
axis([0 8000 -200 200])