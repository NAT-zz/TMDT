// hàm gọi api
function addToCart(id, name, price, image, chip, ram) {
  fetch("/api/add-item-cart", {
    method: "POST",
    body: JSON.stringify({
      product_id: id,
      product_name: name,
      product_price: price,
      product_image: image,
      product_chip: chip,
      product_ram: ram,
    }),
    headers: { "Content-Type": "application/json" },
  })
    .then(function (res) {
      console.info(res);
      return res.json();
    })
    .then(function (data) {
      console.info(data);
      // lấy một thành phần trên html
      // couter đại diện cho nguyên vùng số lượng sản phẩm
      let counter = document.getElementById("cartCounter");
      if (counter !== null) counter.innerText = data.total_quantity;
    });
}

function updateCartItem(obj, productId) {
  fetch("/api/update-cart-item", {
    method: "put",
    body: JSON.stringify({
      product_id: productId,
      quantity: parseInt(obj.value),
    }),
    headers: {
      "Content-Type": "application/json",
    },
  })
    .then(function (res) {
      return res.json();
    })
    .then(function (data) {
      if (data.error_code == 200) {
        let quantity = document.getElementById("cart_quantity");
        let amount = document.getElementById("cart_amount");
        let d = data.cart_stats;
        if (quantity !== null && amount !== null) {
          quantity.innerText = d.total_quantity;
          amount.innerText = d.total_amount;
        }
        let counter = document.getElementById("cartCounter");
        if (counter !== null) counter.innerText = d.total_quantity;
      } else {
        alert("Update Failed");
      }
    });
}

function deleteCartItem(productId) {
  if (confirm("Delete this item ?") == true) {
    fetch("/api/delete-cart-item/" + productId, {
      method: "delete",
    })
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        if (data.error_code == 200) {
          let quantity = document.getElementById("cart_quantity");
          let amount = document.getElementById("cart_amount");
          let d = data.cart_stats;
          if (quantity !== null && amount !== null) {
            quantity.innerText = d.total_quantity;
            amount.innerText = d.total_amount;

            //location.reload()
            let row = document.getElementById("product" + productId);
            row.style.display = "none";
          }
          let counter = document.getElementById("cartCounter");
          if (counter !== null) counter.innerText = d.total_quantity;
        } else {
          alert("Delete failed");
        }
      });
  }
}
function pay(cityname) {
  if (confirm("Confirm payment ?") == true) {
    fetch("/api/pay/" + cityname, {
      method: "post",
    })
      .then(function (res) {
        return res.json();
      })
      .then(function (data) {
        if (data.error_code == 200) {
          alert("Your order have been SAVED!");
          location.reload();
        } else alert("Payment failed");
      });
  }
}

function cancelOrder(id, status = 0) {
  if (confirm("Are you sure?") == true) {
    if (status == 0) {
      fetch("/api/cancel-order", {
        method: "post",
        body: JSON.stringify({
          order_id: id,
        }),
        headers: {
          "Content-Type": "application/json",
        },
      })
        .then(function (res) {
          return res.json();
        })
        .then(function (data) {
          if (data.error_code == 200) {
            alert("Your order was canceled");
            location.reload();
          } else alert("Failed!");
        });
    }
    else if(status == 2 || status == 3){
        fetch("/api/reorder", {
            method: "post",
            body: JSON.stringify({
              order_id: id,
            }),
            headers: {
              "Content-Type": "application/json",
            },
          })
            .then(function (res) {
              return res.json();
            })
            .then(function (data) {
              if (data.error_code == 200) {
                location.replace("/cart");
              } else alert("Failed!");
            });
    }
  }
}
