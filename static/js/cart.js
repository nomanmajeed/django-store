// console.log("Hello Noman");

var updateBtns = document.getElementsByClassName('update-cart')

for (var i=0; i< updateBtns.length; i++){

  updateBtns[i].addEventListener('click', function (){
    var id = this.dataset.product
    var action = this.dataset.action
    console.log('productID: ', id, '\naction:', action)

    console.log(user)
    if (user == 'AnonymousUser') {
      getCookieItem(id, action)
    }else {
      updateUserOrder(id, action)
    }
  })
}

function getCookieItem(productId, action){

  console.log("Guest USer")

  if(action == 'add'){
    if(cart[productId] == undefined){
      cart[productId] = {'quantity' : 1}
    }else{
      cart[productId]['quantity'] += 1
    }
  }

  if(action == 'remove'){
    cart[productId]['quantity'] -= 1

    if(cart[productId]['quantity'] <= 0){
      console.log("Remove Item")
      delete cart[productId]
    }
  }

  console.log("Guest Cart: ", cart)
  document.cookie = 'cart=' + JSON.stringify(cart) + ";domain=;path=/"

  location.reload();

}

function updateUserOrder(productId, action){
  console.log("User is Logged In. sending data....")

  var url='/update_item/'

  // sending data as POST to url and getting response
  fetch(url, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRFToken': csrftoken,
    },
    body: JSON.stringify({'productId':productId, 'action': action})
    //sending data to backend(View.py) via provided url. Data cannot be send as json so we convert it into string using Stringify
  })

  // geting json response from views.py
  .then((response)=>{
    return response.json();
    console.log(response)
  })

  // data get as json response
  .then((data)=>{
    console.log('data: ', data);
    location.reload();
  })

  .catch(function(ex) {
    console.log("parsing failed", ex);
  });


}
