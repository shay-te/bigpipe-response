var FormLogin = createReactClass({
	render: function() {
		var dropdownItems = ["Woman", "Man"];
		return (
			<div>
				<span>{gettext("login_i_am_looking_for")}</span>
				<Dropdown items={dropdownItems} />
				<Button>{gettext("login_singin_with_facebook")}</Button>
			</div>
		);
	}
});


export default FormLogin;