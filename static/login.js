//warn that info is not filled
function validate() {
	// 获得账号
	var account = document.getElementById("account");
	// 获得账号后的span元素用以标记用户输入是否符合要求，放提示信息
	var warn0 = document.getElementById("warn0");
	// 在前台验证
	if (account.value === "") {
		warn0.innerHTML = "Account cannot be null!";
	} 
	else {
		warn0.innerHTML = "√";
	}
	
	// 获得密码
	var password = document.getElementById("password");
	// 获得密码后的span元素
	var warn1 = document.getElementById("warn1");
	// 在前台验证
	if (password.value === "") {
		warn2.innerHTML = "Password cannot be null!";
	} 
	else {
		warn2.innerHTML = "√";
	}
}	

//if info isn't filled cannot submit
function validateForm() {
	// 获得账号
	var account = document.getElementById("account");
	var accountPattern = /^\w+$/;
	// 在前台验证
	if (account.value === "") {
		alert("Please fill in your account.");
		return false;
	}

	// 获得密码
	var password = document.getElementById("password");
	// 密码包含非数字
	var passwordPattern1 = /^\w+$/;// letter _ number
	var passwordPattern2 = /\D/;// match a nonnumeric
	// 在前台验证
	if (password.value === "") {
		alert("Please fill in your password.");
		return false;
	}
	
	//序列化
	function serialize(form){
        
        var parts=[],field=null,i,len;
        for(i=0,len=form.elements.length;i<len;i++){
            field=form.elements[i];
            if(field.name.length){
                parts.push(encodeURIComponent(field.name)+"="+encodeURIComponent(field.value));
            }
        }
        return parts.join("&");
    }
	
	//AJAX
	var xhr=new XMLHttpRequest();
    xhr.open("post","/",false);
    xhr.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
    var login=document.getElementById("login");
    xhr.send(serialize(login));
    var status=xhr.getResponseHeader("LoginStatus");
    if(status===null){
        return true;
    } else {
        alert("Wrong password or account!");
        return false;
    }
}
