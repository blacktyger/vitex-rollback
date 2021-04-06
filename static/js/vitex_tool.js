$(function(){
	$('#button').click(function(){
		var address = $('#address').val();
		var button = $('#button')
		button.prop("disabled", true);
		button.html(
            `Loading... <span style="display: inline-block;
                width: 3rem;
                height: 3rem;
                vertical-align: text-center;
                border: .25em solid currentColor;
                border-right-color: transparent;
                border-radius: 50%;
                -webkit-animation: spinner-border .75s linear infinite;
                animation: spinner-border .75s linear infinite;width: 1rem;
                height: 1rem;
                border-width: .2em;"
            class="spinner-border spinner-border-sm ml-3" role="status" aria-hidden="true"></span>`
        );

		$.ajax({
			url: '/get_account_info',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				console.log(response);
				button.prop("disabled", false);
                button.html(`Check `);

                $('#wallet_today_balance').text(response.wallet.wallet_today_balance);
                $('#wallet_history_balance').text(response.wallet.wallet_history_balance);
                $('#wallet_difference').text(response.wallet.wallet_difference);

                $('#buy_value').text(response.exchange.total_buy);
                $('#sold_value').text(response.exchange.total_sold);
                $('#balance').text(response.exchange.balance);
                $('#participation').text(response.exchange.participation);

                if (response.wallet || response.exchange) {
                    $('#results').toggleClass('epic_hide');
                };
			},
			error: function(error){
				console.log(error);
			}
		});
	});
});
