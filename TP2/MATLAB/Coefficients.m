% Physical Coefficients

m_c =  10;             % kg
m_p =  1;              % kg
l =  0.1;              % m
g = 9.80665;           % m/s2

% Reemplazos introducidos
alpha = m_p + m_c;
lambda = 4/3 * m_p * l^2;
mu = m_p * l;

% Definicion de Amortiguamientos
zeta_c = 0.05;              % adim
zeta_p = 0.01;              % adim

% Frecuencia Natural del pendulo
omega_p = sqrt(mu*g/(lambda-mu^2/alpha));
f_p = omega_p/(2*pi);

% Coeficientes de friccion
beta = 2*zeta_p*omega_p*(lambda-mu^2/alpha);
b = 2*zeta_c*omega_p*alpha;

% Fuerza de equilibrio para caso mas desventajoso
F_equilibrium = 1.5*alpha*g*tand(80);

x_ref = 0;

% Dimensiones del carrito

w_c = 0.05;         % m - Eje X
b_c = 0.1;          % m - Eje Y
h_c = 0.05;         % m - Eje Z

% Dimensiones del pendulo
w_p = 0.025;       % m - Eje X
b_p = 0.025;       % m - Eje Y
h_p = l;           % m - Eje Z
