function ValidaCPF() {
    var RegraValida = document.getElementById("RegraValida").value;
    var cpfValido = /^(([0-9]{3}.[0-9]{3}.[0-9]{3}-[0-9]{2})|([0-9]{11}))$/;
    if (cpfValido.test(RegraValida) == true) {
        console.log("CPF Válido");
    } else {
        console.log("CPF Inválido");
    }
}
function fMasc(objeto, mascara) {
    obj = objeto
    masc = mascara
    setTimeout("fMascEx()", 1)
}

function fMascEx() {
    obj.value = masc(obj.value)
}

function mCPF(cpf) {
    cpf = cpf.replace(/\D/g, "")
    cpf = cpf.replace(/(\d{3})(\d)/, "$1.$2")
    cpf = cpf.replace(/(\d{3})(\d)/, "$1.$2")
    cpf = cpf.replace(/(\d{3})(\d{1,2})$/, "$1-$2")
    return cpf
}

function telefone() {
    var telValido = document.getElementById("telephone").value;
    var telefoneValido = /^(([0-9]{3}.[0-9]{3}.[0-9]{3}-[0-9]{2})|([0-9]{11}))$/;
    if (telefoneValido.test(telValido) == true) {
        console.log("CPF Válido");
    } else {
        console.log("CPF Inválido");
    }
}
function telMasc(objeto, mascara) {
    obje = objeto
    masca = mascara
    setTimeout("telefoneMascEx()", 1)
}

function telefoneMascEx() {
    obje.value = masca(obje.value)
}

function mTEL(tel) {
    tel = tel.replace(/\D/g, "")
    tel = tel.replace(/(\d{2})(\d)/, "($1)$2")
    tel = tel.replace(/(\d{5})(\d)/, "$1$2")
    tel = tel.replace(/(\d{4})(\d)/, "$1$2-")
    return tel
}

function redirect() {
    window.location.assign("semanadafisica.html")
}
