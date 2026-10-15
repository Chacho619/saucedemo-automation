# language: es
Característica: Compra en SauceDemo
  @smoke
  Escenario: Comprar una mochila
    Dado que inicié sesión como usuario estándar
    Cuando agrego "Sauce Labs Backpack" al carrito
    Y completo mis datos de checkout
    Entonces el resumen tiene importes correctos
    Cuando finalizo la compra
    Entonces veo la confirmación de compra

  Esquema del escenario: Rechazar credenciales inválidas
    Cuando intento entrar con el perfil "<perfil>"
    Entonces veo el error "<mensaje>"
    Ejemplos:
      | perfil         | mensaje                                  |
      | locked         | Sorry, this user has been locked out.     |
      | wrong_password | Username and password do not match        |
