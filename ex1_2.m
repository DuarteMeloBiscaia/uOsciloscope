clear all; close all; clc;

% Especificações
f0 = 1000;      % Hz
Q  = 10;
fs = 8000;      % Hz
T  = 1/fs;
w0 = 2*pi*f0;

% Filtro analógico
b_a = [w0/Q 0];
a_a = [1 w0/Q w0^2];

% Transformação bilinear
[b_d, a_d] = bilinear(b_a, a_a, fs);

% Resposta em frequência
f = 0:1:8000;
w_analog = 2*pi*f;

Ta = freqs(b_a, a_a, w_analog);
[Td, w_dig] = freqz(b_d, a_d, 4096, fs);

% Para comparar no mesmo gráfico, usa-se a mesma grelha de frequências
Td2 = freqz(b_d, a_d, w_analog/fs*2*pi);  % resposta digital para ω

Ga = 20*log10(abs(Ta));
Gd = 20*log10(abs(Td2));

phia = angle(Ta)*180/pi;
phid = angle(Td2)*180/pi;

figure(1)
plot(f, Ga, 'linewidth', 2); hold on;
plot(f, Gd, 'linewidth', 2); grid on;
xlabel('Frequency, Hz')
ylabel('Magnitude G(\omega) [dB]')
title('Transfer function of analog and digital filters')
legend('Analog','Digital','location','north')
axis([0 8000 -50 5])

figure(2)
plot(f, phia, 'linewidth', 2); hold on;
plot(f, phid, 'linewidth', 2); grid on;
xlabel('Frequency, Hz')
ylabel('Phase \phi(\omega) [deg]')
title('Phase of analog and digital filters')
legend('Analog','Digital','location','best')
axis([0 8000 -200 200])