<?php

/* PayPal Mobile Checkout Sample PHP - http://www.paypal.com/mobile/

Those who don't have an existing PayPal account:
Go to https://www.paypal.com/uk/mrb/pal=GV8A6PH9C6XVG
Click Sign Up Today.
Set up an account for Business Owners.
Follow the instructions on the PayPal site.

Those who already have a Personal or Premier account:

Go to https://www.paypal.com/uk/mrb/pal=GV8A6PH9C6XVG
Click the Upgrade your Account link.
Click the Upgrade Now button.
Choose to upgrade to a Business account and follow instructions to complete the upgrade.
If you haven't already, add a bank account to become a Verified member. Follow the instructions on the PayPal site. This process may take 2-3 business days.

-- 

step 1 - configure your account for mobile checkout - paypal > profile > api access > edit / create > tick SetMobileCheckout and DoMobileCheckoutPayment
step 2 - configure your api username, password and signature in constants.php
step 3 - upload, test and integrate with your mobile site - when you want to go live comment out the sandbox value below

mobile checkout is pretty simple, you submit some variables to paypal and they return a token
you use this token when you direct your customer to paypal to confirm the payment
once the customer has paid they're sent back to you with the same token attached

mobile checkout developer guide - https://www.paypal.com/en_US/pdf/PP_MobileCheckout.pdf
integration center - http://www.paypal.com/IntegrationCenter/ic_mobile-checkout.html
paypal mobile forum - http://www.pdncommunity.com/pdn/board?board.id=mobile

this script was originally based on ReviewOrder.php from the paypal php nvp sdk
CallerService.php and constants.php are from the sdk though constants has been changed to switch sandbox on and off and use the mobile urls
original unaltered copies can be downloaded from http://www.paypal.com/sdk/
the latest version of this script can be found at http://www.andymoore.info/paypal-mobile-checkout-php/

Andy Moore
dotMobi Certified Mobile Web Developer
http://www.andymoore.info/
*/

// do you want to test on the sandbox? set to yes or comment this line to go live
$sandbox = 'yes';

// initialise the session
session_start();

// include the file with the api functions (which subsequently includes constants.php)
include('CallerService.php');

// if token is not set or is empty we perform SetMobileCheckout - otherwise we're processing DoMobileCheckoutPayment
if(!isset($_REQUEST['token'])||$_REQUEST['token']==''){

  // build up the values we will submit for this order
  // in the most basic form this only needs AMT CURRENCYCODE DESC RETURNURL AND CANCELURL paramaters passing - everything else is optional

  $submit_string .= '&AMT=1.00'; // REQUIRED - Cost of the item before tax and shipping. Must not exceed $1,000 USD in any currency. No currency symbol, decimal seperator must be a point '.'  optional thousands seperator ','
  $submit_string .= '&CURRENCYCODE=GBP'; // REQUIRED - three character currency code. Accepts the following values: AUD / CAD / EUR / GBP / JPY / USD
  $submit_string .= '&DESC=Product+Description'; // REQUIRED - the name of the item being offered <127 characters
  $submit_string .= '&RETURNURL='.urlencode('http://'.$_SERVER['HTTP_HOST'].$_SERVER['REQUEST_URI']); // REQUIRED - urlencoded value - where the customer is directed to post paypal - ?token=123456789 will be added - it's suggested to make it the final review page prior to ordering
  $submit_string .= '&CANCELURL='.urlencode('http://'.$_SERVER['HTTP_HOST'].$_SERVER['REQUEST_URI']); // REQUIRED - urlencoded value - where the customer is directed to if they click the cancel or return to merchant links at paypal

  // $submit_string = '&PHONENUM='; // OPTIONAL - Localized phone number used by the buyer to submit their payment request. If the phone number is activated for mobile checkout PayPal will use it to pre-propagate the login page - 9 to 13 numeric characters
  // $submit_string .= '&TAXAMT='; // OPTIONAL - tax on item purchased
  // $submit_string .= '&SHIPPINGAMT='; // OPTIONAL - the shipping cost for this transaction
  // $submit_string .= '&NUMBER='; // OPTIONAL - pass through value, returned verbatin on DoMobileCheckoutPayment - for values like stock keeping units <127 single byte characters
  // $submit_string .= '&CUSTOM='; // OPTIONAL - pass through value, returned verbatin on DoMobileCheckoutPayment - store session IDs and other values here <256 characters
  // $submit_string .= '&INVNUM='.time(); // OPTIONAL - Your own invoice number of ID used to identify the transaction. <127 single byte characters - must be unique
  // $submit_string .= '&ADDRESSDISPLAY=1'; // OPTIONAL - 0 = shipping address not required or 1 = an address is required, address displayed by default - must be 1 for physical goods - users can't edit the address though they can select from other addresses on file at paypal
  // $submit_string .= '&SHAREPHONENUM=0'; // OPTIONAL - indicates if the customer's phone number is to be returned to the merchant. The customer will be notified during the flow and given the opportunity to override this
  // $submit_string .= '&EMAIL='; // OPTIONAL - email address of the buyer as entered during checkout. If the phone number is not mobile activated this is used to pre-fill the login form <127 single byte characters

  // these values let you set the customer's shipping address, if an address is specified it is displayed during checkout, if not the customers default shipping address will be shown
  // these values are only applicable if ADDRESSDISPLAY=1
  // $submit_string .= '&SHIPTOCITY=';// REQUIRED - name of the city <120 single byte characters
  // $submit_string .= '&SHIPTOSTATE=';// OPTIONAL - name of the state or province <120 single byte characters
  // $submit_string .= '&SHIPTOCOUNTRY=';// REQUIRED - iso 3166 country code - examples US CA UK - two single byte characters
  // $submit_string .= '&SHIPTOZIP=';// OPTIONAL - us zip code or other country specific postal code <20 single byte characters

  // perform the api callback for SetMobileCheckout with those values 
  $resArray = hash_call('SetMobileCheckout',$submit_string);

  // if we get an acknowledgement of SUCCESS there should also be a valid token
  if(strtoupper($resArray['ACK'])=='SUCCESS'){
    // redirect the customer to paypal to confirm the payment, pass the token value in the url - tokens expire after three hours (20 single byte characters)
    header('Location: '.PAYPAL_URL.urldecode($resArray['TOKEN']));
  }else{
    // SetMobileCheckout failed
    echo 'SetMobileCheckout failed: '.$resArray['L_SHORTMESSAGE0'].' '.$resArray['L_ERRORCODE0'].' '.$resArray['L_LONGMESSAGE0'];
  }

// ends no token or empty token value / ends performing SetMobileCheckout
}else{
// starts processing token to call DoMobileCheckOutPayment to complete the transaction and collect the users details 
// if you don't do DoMobileCheckoutPayment you don't get the funds

  // submit the token value to paypal with the DoMobileCheckoutPayment callback
  $resArray = hash_call('DoMobileCheckoutPayment','&token='.$_REQUEST['token']);

  // run an if against the ACK value - it'll return either SUCCESS or FAILURE
  if(strtoupper($resArray['ACK'])=='SUCCESS'){
    echo 'DoMobileCheckoutPayment success: '.$resArray['CURRENCYCODE'].' '.$resArray['AMT'].' from '.$resArray['EMAIL'].' ('.$resArray['FIRSTNAME'].' '.$resArray['LASTNAME'].')';

    // values to read are: (if you have instant payment notification running paypal will post you these values to your regular ipn handler)

    // CUSTOM - pass through value returned from SetMobileCheckout
    // INVNUM - pass through value return from SetMobileCheckout
    // TRANSACTIONID - unique transaction ID for this order, 19 single byte characters
    // PARENTTRANSACTIONID - (should always be empty) parent or related TRANSACTIONID - processed for the following transaction types: Reversal, Capture of an authorised transaction, Reauthorisation of a transaction, Capture of an order, Authorisation of an order (in both those cases the PARENTTRANSACTION is the original order id) Capture of an order authorisation, void of an order. - 16 single byte characters in xxxx-xxxx-xxxx-xxxxm format
    // RECEIPTID - receipt indentification 16 single byte numbers in xxxx-xxxx-xxxx-xxxx format
    // TRANSACTIONTYPE - the type of transaction, with PPMC only send-money will be passed
    // PAYMENTTYPE - indicates if the payment is instant or delayed, values are none and instant
    // ORDERTIME - the time and date of the order
    // AMT - the full order ammount before transaction fees are deducted - <$1000 USD in any currency
    // CURRENCYCODE - the currency passed in SetMobileCheckout - this is oddly listed in the spec four times.......
    // FEEAMT - the ammount PayPal charged to process this transaction
    // SETTLEAMT - how much from the transaction will be deposited into your PayPal account
    // TAXAMT - the tax charged on the transaction as specified in SetMobileCheckout
    // EXCHANGERATE - exchange rate if any currency conversion occured 
    // PAYMENTSTATUS - status of the order with PayPal will be either Completed or Pending - if pending see PENDINGREASON below - can also be Reversed tho not listed in the docs
    // PENDINGREASON - the reason the payment is pending: none, address, intl, multi-currency, verify, unilateral, upgrade, other - see the docs for a full breakdown of each
    // REASONCODE - only applicable if the transaction has been reversed (PAYMENTSTATUS is Reversed)
    // EMAIL - the buyers email address

    // PayerInfo values:
    // PAYERID - unique customer account number for that customer
    // PAYERSTATUS - status of the payer's email address
    // COUNTRYCODE - iso 3166 country code
    // BUSINESS - payer's business name
    // PHONENUM - phone number shared by the customer with the merchant, see notes above about how the customer can deny this

    // PayerName values:
    // SALUTATION - the payer's salutation
    // FIRSTNAME - first name
    // MIDDLENAME - middle name
    // LASTNAME - surname
    // SUFFIX - suffix

    // AddressType values - only if DISPLAYADDRESS=1
    // NAME - the persons name associated with that shipping address
    // SHIPTOSTREET - street address line 1 
    // SHIPTOSTREET2 - street address line 2 
    // SHIPTOCITY - name of city
    // SHIPTOSTATE - name of state or province
    // SHIPTOCOUNTRY - ISO 3166 country code
    // SHIPTOZIP - us zip code or other country specific postal code
    // SHIPTOPHONENUM - the phone number associated with this address
    // ADDRESSOWNER - ebay company which maintains this address, either eBay or PayPal
    // ADDRESSSTATUS - status of the address on file with PayPal - either None, Confirmed or Unconfirmed
  
  // ends SUCCESS 
  }else{
    // DoMobileCheckoutPayment failed
    echo 'DoMobileCheckoutPayment failed '.$resArray['L_SHORTMESSAGE0'].' '.$resArray['L_ERRORCODE0'].' '.$resArray['L_LONGMESSAGE0'];
  }

// ends processing the DoMobileCheckoutPayment callback
}

?>
