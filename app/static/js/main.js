console.log('Mensaje desde mi nuevo servidor de flask');

window.setTimeout(function(){
    $("#alerta").fadeTo(1500, 0).slideDown(1000,
    function(){
        $(this).remove();
    });
}, 2000);