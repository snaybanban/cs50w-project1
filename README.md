# Project 1

Web Programming with Python and JavaScript

Este proyecto esta creado para valorar libros, se usa una API de google para comentar y darle una valoracion. primero la pagina pide un usuario y una clave, si no esta ese usuario registrado en la base de datos saldra error, pero se puede crear un usuario y ser redigido a la pagina de busqueda. para buscar un libro se puede hacer mediante el ombre o el isbn para dar mejor resultado. si el libro esta correcto mandara una peticion para mandar a traer ese libro de la API y mostrar informacion de el. podemos ver la portada, mas descripcion de el y ademas podremos comentarlo y valorarlo.

posee diferentes rutas para navegar comodamente y hacer buen uso de flask. cada ruta esta debidamente enlazada por lo tanto, login: para iniciar session, register: por si no hay un usuario lo registramos, layout: para cargar la pagina principal de todo el proyecto, cambio: para cambiar la contraseña al usuario actual, index: para buscar el libro, error/erro2: para informar que algo ha salido mal, book: para mostrar la descripcion del libro y valorar y comentar, quote: para cuando se cierre session.
