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
        $('#loading_info').toggleClass('epic_hide');

		$.ajax({
			url: '/get_account_info',
			data: $('form').serialize(),
			type: 'POST',
			success: function(response){
				console.log(response);
				$('#loading_info').toggleClass('epic_hide')
				button.prop("disabled", false);
                button.html(`Check `);

                $('#wallet_today_balance').text(response.wallet.wallet_today_balance.toLocaleString('en-US'));
                $('#wallet_history_balance').text(response.wallet.wallet_history_balance.toLocaleString('en-US'));
                $('#wallet_difference').text(response.wallet.wallet_difference.toLocaleString('en-US'));

                $('#buy_value').text(response.exchange.total_buy.toLocaleString('en-US'));
                $('#sold_value').text(response.exchange.total_sold.toLocaleString('en-US'));
                $('#balance').text(response.exchange.balance.toLocaleString('en-US'));
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
