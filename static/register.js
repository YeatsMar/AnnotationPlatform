//在前台检查用户输入的注册信息的函数
//validate
function validate() {
	// 获得账号
	var account = document.getElementById("account");
	// 获得账号后的span元素用以标记用户输入是否符合要求，放提示信息
	var warn0 = document.getElementById("warn0");
	var accountPattern = /^(\w)+(\.\w+)*@(\w)+((\.\w+)+)$/;// pattern for email
	// 在前台验证
	if (account.value === "") {
		warn0.innerHTML = "账号不得为空！";
        return false;
	} else if (!accountPattern.test(account.value)) {
		warn0.innerHTML = "邮箱格式不正确！";
        return false;
	} else if (account.value.length >= 45) {
		warn0.innerHTML = "邮箱字符少于45位！";
        return false;
	}
	else {
		warn0.innerHTML = "√";
	}

	// 获得姓名
	var username = document.getElementById("username");
	// 获得姓名后的span元素
	var warn1 = document.getElementById("warn1");
	// 在前台验证
	if (username.value === "") {
		warn1.innerHTML = "账号不得为空！";
		return false;
	} else {
		warn1.innerHTML = "√";
	}

	// 获得密码
	var password = document.getElementById("password");
	// 获得密码后的span元素
	var warn2 = document.getElementById("warn2");
	// 密码只能是英文、数字或符号
	var passwordPattern1 = /^\w+$/;
	var passwordPattern2 = /\D/;// match only one can return true
	// 在前台验证
	if (password.value === "") {
		warn2.innerHTML = "密码不得为空！";
		return false;
	} else {
		warn2.innerHTML = "√";
	}

	// 获得确认密码
	var passwordRepeat = document.getElementById("passwordRepeat");
	// 获得密码后的span元素
	var warn3 = document.getElementById("warn3");
	// 在前台验证
	if (passwordRepeat.value === password.value) {
		warn3.innerHTML = "√";
	} else {
		warn3.innerHTML = "密码不一致！";
		return false;
	}
	return true;
}

// 在表单提交之前进行的验证
function validateForm() {

	if (validate()) {
		function serialize(form) {// serialize an element: name=value

			var parts = [], field = null, i, len;// parts is an array, field is an object, synchronously declare these 4 variable
			for (i = 0, len = form.elements.length; i < len; i++) {
				field = form.elements[i];
				if (field.name.length) {// if the element of the form has "name"attribute
					parts.push(encodeURIComponent(field.name) + "="
							+ encodeURIComponent(field.value));
				}
			}
			return parts.join("&");// return a String instead of as Array
		}
		// 验证账户唯一 todo
		var xhr = new XMLHttpRequest();
		xhr.open("post", "/registerpage", false);
        xhr.setRequestHeader("ValidateAccount","true");
        xhr.setRequestHeader("Content-Type","application/x-www-form-urlencoded");
		var form = document.getElementById("register");
		xhr.send(serialize(form));//wait for servlet
		var status = xhr.getResponseHeader("RegisterStatus");
		if (!(status === null)) {
			alert("帐号重复！");
			return false;
		}
		return true;
	} else {
		alert("填写错误!");
		return false;
	}

}
