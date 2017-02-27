/**
 * Created by mayezhou on 2017/2/17.
 */

//if info isn't filled cannot submit
function validateForm() {
    var label = document.getElementsByName("label");
    if (label.length === 0) {
		alert("Have not labeled!");
		return false;
	}
}