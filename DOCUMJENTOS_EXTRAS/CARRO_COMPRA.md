
# Carro de la compra

    por[Erik Reitan](https://github.com/Erikre)

[Descarga del proyecto de ejemplo (C#) Wingtip Toys](https://go.microsoft.com/fwlink/?LinkID=389434&clcid=0x409) o [Descarga del libro electrónico (PDF)](https://download.microsoft.com/download/0/F/B/0FBFAA46-2BFD-478F-8E56-7BF3C672DF9D/Getting%20Started%20with%20ASP.NET%204.5%20Web%20Forms%20and%20Visual%20Studio%202013.pdf)

> En esta serie de tutoriales se enseñan los conceptos básicos de la
> compilación de una aplicación ASP.NET Web Forms mediante ASP.NET 4.5 y
> Microsoft Visual Studio Express 2013 para Web. Como acompañamiento a
> esta serie de tutoriales, hay disponible un [proyecto con código fuente de C#](https://go.microsoft.com/fwlink/?LinkID=389434&clcid=0x409) de Visual Studio 2013.

En este tutorial se describe la lógica de negocios necesaria para
agregar un carro de la compra a la aplicación de ejemplo Wingtip Toys de
 ASP.NET Web Forms. Este tutorial se basa en el tutorial anterior
"Mostrar los elementos de datos y los detalles" y forma parte de la
serie de tutoriales de Wingtip Toy Store. Cuando haya completado este
tutorial, los usuarios de la aplicación de ejemplo podrán agregar,
quitar y modificar los productos en su carro de la compra.

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#what-youll-learn)## Temas que se abordarán:

1. Cómo crear un carro de la compra para la aplicación web.
2. Cómo permitir que los usuarios agreguen elementos al carro de la compra.
3. Cómo agregar un control [GridView](https://msdn.microsoft.com/library/system.web.ui.webcontrols.gridview(v=vs.110).aspx#introduction) para mostrar los detalles del carro de la compra.
4. Cómo calcular y mostrar el total del pedido.
5. Cómo quitar y actualizar elementos en el carro de la compra.
6. Cómo incluir un contador de carro de la compra.

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#code-features-in-this-tutorial)## Características de código de este tutorial:

1. Entity Framework Code First
2. Anotaciones de datos
3. Controles de datos fuertemente tipados
4. Enlace de modelos

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#creating-a-shopping-cart)## Creación de un carro de la compra

Anteriormente en esta serie de tutoriales, agregó páginas y código
para ver los datos del producto de una base de datos. En este tutorial,
creará un carro de la compra para administrar los productos que los
usuarios están interesados en comprar. Los usuarios podrán examinar y
agregar elementos al carro de la compra incluso si no están registrados o
 conectados. Para administrar el acceso al carro de la compra, asignará a
 los usuarios un único `ID` mediante un identificador único global (GUID) cuando el usuario acceda al carro de la compra por primera vez. Almacenará este `ID` mediante el estado de sesión de ASP.NET.

 Nota:

El estado de sesión ASP.NET es un lugar cómodo para almacenar
información específica del usuario que caducará después de que el
usuario salga del sitio. Aunque el uso incorrecto del estado de sesión
pueda tener implicaciones de rendimiento en sitios más grandes, su uso
ligero funciona bien con fines de demostración. El proyecto de ejemplo
Wingtip Toys muestra cómo usar el estado de sesión sin un proveedor
externo, donde el estado de sesión se almacena In-Process en el servidor
 web que hospeda el sitio. En el caso de los sitios más grandes que
proporcionan varias instancias de una aplicación o de los sitios que
ejecutan varias instancias de una aplicación en servidores diferentes,
considere la posibilidad de usar  **Windows Azure Cache Service** .
 Este servicio de caché proporciona un servicio de almacenamiento en
caché distribuido externo al sitio web y resuelve el problema de usar el
 estado de sesión en proceso. Para obtener más información, consulte [Uso del estado de sesión de ASP.NET con sitios web de Windows Azure](https://learn.microsoft.com/es-es/azure/redis-cache/cache-aspnet-session-state-provider).

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#add-cartitem-as-a-model-class)### Agregar CartItem como una clase de modelo

Anteriormente en esta serie de tutoriales, definió el esquema para
los datos de categorías y productos mediante la creación de las clases
de `Category` y `Product` en la carpeta  *Modelos* .
 Ahora, agregue una nueva clase para definir el esquema del carro de la
compra. Más adelante en este tutorial, agregará una clase para controlar
 el acceso a los datos de la tabla `CartItem`. En esta clase se proporcionará la lógica de negocios para agregar, quitar y actualizar elementos en el carro de la compra.

1. Haga clic con el botón derecho en la carpeta *Modelos* y, luego, seleccione **Agregar** ->  **Nuevo elemento** .
   ![Shopping Cart - New Item](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart/_static/image1.png)
2. Se abrirá el cuadro de diálogo  **Agregar nuevo elemento** . Seleccione **Código** y, a continuación, seleccione  **Clase** .
   ![Shopping Cart - Add New Item Dialog](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart/_static/image2.png)
3. Asigne a esta nueva clase el nombre  *CartItem.cs* .
4. Haga clic en  **Agregar** .

   El nuevo archivo de la clase se mostrará en el editor.
5. Reemplace el código predeterminado por el siguiente:

   **C#**
6. ```
   using System.ComponentModel.DataAnnotations;

   namespace WingtipToys.Models
   {
       public class CartItem
       {
           [Key]
           public string ItemId { get; set; }

           public string CartId { get; set; }

           public int Quantity { get; set; }

           public System.DateTime DateCreated { get; set; }

           public int ProductId { get; set; }

           public virtual Product Product { get; set; }

       }
   }
   ```

La clase de `CartItem` contiene el esquema que definirá
cada producto que agreguen los usuarios al carro de la compra. Esta
clase es similar a las otras clases de esquema que creó anteriormente en
 esta serie de tutoriales. Por convención, Entity Framework Code First
espera que la clave principal de la tabla `CartItem` sea `CartItemId` o `ID`. Sin embargo, el código invalida el comportamiento predeterminado mediante el atributo de anotación de datos `[Key]`. El atributo `Key` de la propiedad ItemId especifica que la propiedad `ItemID` es la clave principal.

La propiedad `CartId` especifica el `ID` del usuario asociado al elemento que se va a comprar. Agregará código para crear este usuario `ID` cuando el usuario acceda al carro de la compra. Este `ID` también se almacenará como una variable de ASP.NET Session.

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#update-the-product-context)### Actualizar el contexto del producto

Aparte de agregar la clase de `CartItem`, debe actualizar
la clase de contexto de la base de datos que administra las clases de
entidad y que proporciona acceso a los datos de la base de datos. Para
ello, agregará la clase del modelo de `CartItem` recién creada a la clase de `ProductContext`.

1. En el  **Explorador de soluciones** , busque y abra el archivo *ProductContext.cs* en la carpeta  *Modelos* .
2. Agregue el código resaltado al archivo *ProductContext.cs* como se muestra a continuación:

   **C#**
3. ```
   using System.Data.Entity;

   namespace WingtipToys.Models
   {
       public class ProductContext : DbContext
       {
           public ProductContext()
               : base("WingtipToys")
           {
           }

           public DbSet<Category> Categories { get; set; }
           public DbSet<Product> Products { get; set; }
           public DbSet<CartItem> ShoppingCartItems { get; set; }
       }
   }
   ```

Tal y como se mencionó anteriormente en esta serie de tutoriales, el código del archivo *ProductContext.cs* agrega el espacio de nombres de servicio `System.Data.Entity`
 para que tenga acceso a todas las funcionalidades principales de Entity
 Framework. Esta funcionalidad incluye la capacidad de consultar,
insertar, actualizar y eliminar datos usando objetos fuertemente
tipados. La clase de `ProductContext` agrega acceso a la clase del modelo `CartItem` recién agregada.

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#managing-the-shopping-cart-business-logic)### Administración de la lógica de negocios del carro de la compra

A continuación, creará la clase de `ShoppingCart` en una nueva carpeta  *Logic* . La clase de `ShoppingCart` controla el acceso a los datos de la tabla `CartItem`. La clase también incluirá la lógica de negocios para agregar, quitar y actualizar elementos en el carro de la compra.

La lógica del carro de la compra que agregará contendrá la funcionalidad para administrar las siguientes acciones:

1. Agregar elementos al carro de la compra
2. Quitar elementos del carro de la compra
3. Obtener el id. del carro de la compra
4. Recuperar elementos del carro de la compra
5. Sumar el total de la cantidad de elementos del carro de la compra
6. Actualizar los datos del carro de la compra

Una página del carro de la compra ( *ShoppingCart.aspx* ) y la
clase del carro de la compra se usarán juntas para acceder a los datos
del carro de la compra. La página del carro de la compra mostrará todos
los elementos que el usuario agregue al carro de la compra. Además de la
 página y la clase del carro de la compra, creará una página ( *AddToCart.aspx* ) para agregar productos al carro de la compra. También agregará código a las páginas *ProductList.aspx* y *ProductDetails.aspx* que proporcionará un vínculo a la página *AddToCart.aspx* para que el usuario pueda agregar productos al carro de la compra.

En el diagrama siguiente se muestra el proceso básico que se produce cuando el usuario agrega un producto al carro de la compra.

![Shopping Cart - Adding to the Shopping Cart](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart/_static/image3.png)

Cuando el usuario hace clic en el vínculo **Agregar al carro** de las páginas *ProductList.aspx* o  *ProductDetails.aspx* , la aplicación navegará a la página *AddToCart.aspx* y, a continuación, automáticamente a  *ShoppingCart.aspx* . La página *AddToCart.aspx* agregará el producto seleccionado al carro de la compra llamando a un método en la clase ShoppingCart. La página *ShoppingCart.aspx* mostrará los productos que se han agregado al carro de la compra.

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#creating-the-shopping-cart-class)#### Crear la clase del carro de la compra

La clase de `ShoppingCart` se agregará a una carpeta
independiente en la aplicación para que haya una distinción clara entre
el modelo (carpeta Modelos), las páginas (carpeta raíz) y la lógica
(carpeta Lógica).

1. En el **Explorador de soluciones** haga clic con el botón derecho en el proyecto **WingtipToys** y seleccione  **Agregar** -> **Nueva carpeta** . Asigne el nombre *Lógica* a la nueva carpeta.
2. Haga clic con el botón derecho en la carpeta *Lógica* y, luego, seleccione **Agregar** -> **Nuevo elemento** .
3. Agregue un nuevo archivo de clase denominado  *ShoppingCartActions.cs* .
4. Reemplace el código predeterminado por el siguiente:

   **C#**
5. ```
   using System;
   using System.Collections.Generic;
   using System.Linq;
   using System.Web;
   using WingtipToys.Models;

   namespace WingtipToys.Logic
   {
     public class ShoppingCartActions : IDisposable
     {
       public string ShoppingCartId { get; set; }

       private ProductContext _db = new ProductContext();

       public const string CartSessionKey = "CartId";

       public void AddToCart(int id)
       {
         // Retrieve the product from the database.         
         ShoppingCartId = GetCartId();

         var cartItem = _db.ShoppingCartItems.SingleOrDefault(
             c => c.CartId == ShoppingCartId
             && c.ProductId == id);
         if (cartItem == null)
         {
           // Create a new cart item if no cart item exists.               
           cartItem = new CartItem
           {
             ItemId = Guid.NewGuid().ToString(),
             ProductId = id,
             CartId = ShoppingCartId,
             Product = _db.Products.SingleOrDefault(
              p => p.ProductID == id),
             Quantity = 1,
             DateCreated = DateTime.Now
           };

           _db.ShoppingCartItems.Add(cartItem);
         }
         else
         {
           // If the item does exist in the cart,                
           // then add one to the quantity.               
           cartItem.Quantity++;
         }
         _db.SaveChanges();
       }

       public void Dispose()
       {
         if (_db != null)
         {
           _db.Dispose();
           _db = null;
         }
       }

       public string GetCartId()
       {
         if (HttpContext.Current.Session[CartSessionKey] == null)
         {
           if (!string.IsNullOrWhiteSpace(HttpContext.Current.User.Identity.Name))
           {
             HttpContext.Current.Session[CartSessionKey] = HttpContext.Current.User.Identity.Name;
           }
           else
           {
             // Generate a new random GUID using System.Guid class.   
             Guid tempCartId = Guid.NewGuid();
             HttpContext.Current.Session[CartSessionKey] = tempCartId.ToString();
           }
         }
         return HttpContext.Current.Session[CartSessionKey].ToString();
       }

       public List<CartItem> GetCartItems()
       {
         ShoppingCartId = GetCartId();

         return _db.ShoppingCartItems.Where(
             c => c.CartId == ShoppingCartId).ToList();
       }
     }
   }
   ```

El método `AddToCart` permite incluir productos individuales en el carro de la compra en función del producto `ID`. El producto se agrega al carro o se incrementa la cantidad del producto si el carro ya lo contiene.

El método `GetCartId` devuelve el carro `ID` para el usuario. El carro `ID`
 se utiliza para realizar un seguimiento de los elementos que un usuario
 tiene en su carro de la compra. Si el usuario no tiene un carro `ID`existente, se crea un carro `ID` nuevo para el. Si el usuario ha iniciado sesión como usuario registrado, el carro `ID` se establece en su nombre de usuario. Sin embargo, si el usuario no ha iniciado sesión, el carro `ID`
 se establece en un valor único (un GUID). Un GUID garantiza que solo se
 cree un carro para cada usuario, en función de la sesión.

El método `GetCartItems` devuelve una lista de elementos
de carro de la compra para el usuario. Más adelante en este tutorial,
verá que el enlace de modelos se usa para mostrar los elementos del
carro en el carro de la compra mediante el método `GetCartItems`.

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#creating-the-add-to-cart-functionality)### Creación de la funcionalidad de agregar al carro

Como se mencionó anteriormente, creará una página de procesamiento denominada *AddToCart.aspx* que se usará para agregar nuevos productos al carro de la compra del usuario. Esta página llamará al método `AddToCart` en la clase de `ShoppingCart` que acaba de crear. La página *AddToCart.aspx* esperará que se le pase un producto `ID`. Este producto `ID` se usará al llamar al método `AddToCart` en la clase de `ShoppingCart`.

 Nota:

Va a modificar el código subyacente ( *AddToCart.aspx.cs* ) de esta página, no la interfaz de usuario de la página ( *AddToCart.aspx* ).

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#to-create-the-add-to-cart-functionality)#### Creación de la funcionalidad de agregar al carro:

1. En  **Explorador de soluciones** , haga clic con el botón derecho en el proyecto **WingtipToys** y después haga clic en **Añadir** -> **Nuevo elemento** .

   Se abrirá el cuadro de diálogo  **Agregar nuevo elemento** .
2. Agregue una nueva página estándar (formulario web) a la aplicación denominada  *AddToCart.aspx* .
   ![Shopping Cart - Add Web Form](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart/_static/image4.png)
3. En el  **Explorador de soluciones** , haga clic con el botón derecho en la página *AddToCart.aspx* y, después, haga clic en  **Ver código** . El archivo de código subyacente *AddToCart.aspx.cs* se abre en el editor.
4. Reemplace el código existente en el archivo de código subyacente *AddToCart.aspx.cs* por el código siguiente:

   **C#**
5. ```
   using System;
   using System.Collections.Generic;
   using System.Linq;
   using System.Web;
   using System.Web.UI;
   using System.Web.UI.WebControls;
   using System.Diagnostics;
   using WingtipToys.Logic;

   namespace WingtipToys
   {
     public partial class AddToCart : System.Web.UI.Page
     {
       protected void Page_Load(object sender, EventArgs e)
       {
         string rawId = Request.QueryString["ProductID"];
         int productId;
         if (!String.IsNullOrEmpty(rawId) && int.TryParse(rawId, out productId))
         {
           using (ShoppingCartActions usersShoppingCart = new ShoppingCartActions())
           {
             usersShoppingCart.AddToCart(Convert.ToInt16(rawId));
           }

         }
         else
         {
           Debug.Fail("ERROR : We should never get to AddToCart.aspx without a ProductId.");
           throw new Exception("ERROR : It is illegal to load AddToCart.aspx without setting a ProductId.");
         }
         Response.Redirect("ShoppingCart.aspx");
       }
     }
   }
   ```

Cuando se carga la página  *AddToCart.aspx* , el producto `ID`
 se recupera de la cadena de consulta. A continuación, se crea una
instancia de la clase de carro de la compra y se usa para llamar al
método `AddToCart` que agregó anteriormente en este tutorial. El método `AddToCart`, comprendido en el archivo  *ShoppingCartActions.cs* ,
 incluye la lógica para agregar el producto seleccionado al carro de la
compra o incrementar la cantidad del producto seleccionado. Si el
producto no se ha agregado al carro de la compra, se agrega a la tabla `CartItem`
 de la base de datos. Si el producto ya se ha agregado al carro de la
compra y el usuario agrega otro artículo del mismo producto, la cantidad
 del producto se incrementa en la tabla `CartItem`. Por último, la página vuelve a redirigir a la página *ShoppingCart.aspx* que agregará en el paso siguiente, donde el usuario ve una lista actualizada de los elementos que están en el carro.

Como se mencionó anteriormente, se usa un usuario `ID` para identificar los productos asociados a un usuario específico. Este `ID` se agrega a una fila de la tabla `CartItem` cada vez que el usuario agrega un producto al carro de la compra.

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#creating-the-shopping-cart-ui)### Creación de la interfaz de usuario del carro de la compra

La página *ShoppingCart.aspx* mostrará los productos que se
han agregado al carro de la compra. También proporcionará la capacidad
de agregar, quitar y actualizar elementos en el carro de la compra.

1. En el  **Explorador de soluciones** , haga clic con el botón derecho en  **WingtipToys** , haga clic en **Agregar** -> **Nuevo elemento** .

   Se abrirá el cuadro de diálogo  **Agregar nuevo elemento** .
2. Seleccione **Formulario web mediante la página maestra** para agregar una nueva página (formulario web) que incluya una página maestra. Denomine a la nueva página  *ShoppingCart.aspx* .
3. Seleccione **Site.Master** para adjuntar la página maestra a la página *.aspx* recién creada.
4. En la página  *ShoppingCart.aspx* , reemplace el marcado existente por el marcado siguiente:

   **ASP.NET**
5. ```
   <%@ Page Title="" Language="C#" MasterPageFile="~/Site.Master" AutoEventWireup="true" CodeBehind="ShoppingCart.aspx.cs" Inherits="WingtipToys.ShoppingCart" %>
   <asp:Content ID="Content1" ContentPlaceHolderID="MainContent" runat="server">
       <div id="ShoppingCartTitle" runat="server" class="ContentHead"><h1>Shopping Cart</h1></div>
       <asp:GridView ID="CartList" runat="server" AutoGenerateColumns="False" ShowFooter="True" GridLines="Vertical" CellPadding="4"
           ItemType="WingtipToys.Models.CartItem" SelectMethod="GetShoppingCartItems" 
           CssClass="table table-striped table-bordered" >   
           <Columns>
           <asp:BoundField DataField="ProductID" HeaderText="ID" SortExpression="ProductID" />      
           <asp:BoundField DataField="Product.ProductName" HeaderText="Name" />      
           <asp:BoundField DataField="Product.UnitPrice" HeaderText="Price (each)" DataFormatString="{0:c}"/>   
           <asp:TemplateField   HeaderText="Quantity">          
                   <ItemTemplate>
                       <asp:TextBox ID="PurchaseQuantity" Width="40" runat="server" Text="<%#: Item.Quantity %>"></asp:TextBox> 
                   </ItemTemplate>      
           </asp:TemplateField>  
           <asp:TemplateField HeaderText="Item Total">          
                   <ItemTemplate>
                       <%#: String.Format("{0:c}", ((Convert.ToDouble(Item.Quantity)) *  Convert.ToDouble(Item.Product.UnitPrice)))%>
                   </ItemTemplate>      
           </asp:TemplateField> 
           <asp:TemplateField HeaderText="Remove Item">          
                   <ItemTemplate>
                       <asp:CheckBox id="Remove" runat="server"></asp:CheckBox>
                   </ItemTemplate>      
           </asp:TemplateField>  
           </Columns>  
       </asp:GridView>
       <div>
           <p></p>
           <strong>
               <asp:Label ID="LabelTotalText" runat="server" Text="Order Total: "></asp:Label>
               <asp:Label ID="lblTotal" runat="server" EnableViewState="false"></asp:Label>
           </strong> 
       </div>
       <br />
   </asp:Content>
   ```

La página *ShoppingCart.aspx* incluye un control **GridView** denominado `CartList`. Este control usa el enlace de modelos para enlazar los datos del carro de la compra desde la base de datos al control  **GridView** . Al establecer la propiedad de `ItemType` del control  **GridView** , la expresión de enlace de datos `Item`
 está disponible en el marcado del control y el control se vuelve
fuertemente tipado. Como se mencionó anteriormente en esta serie de
tutoriales, puede seleccionar los detalles del objeto de `Item`
 mediante IntelliSense. Para configurar un control de datos con el fin
de usar el enlace de modelos para seleccionar datos, defina la propiedad
 de `SelectMethod` del control. En el marcado anterior, configura `SelectMethod` para que use el método GetShoppingCartItems que devuelve una lista de objetos `CartItem`. El control de datos **GridView**
 llama al método en el momento adecuado del ciclo de vida de la página y
 automáticamente enlaza los datos que se devuelven. El método `GetShoppingCartItems` todavía debe agregarse.

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#retrieving-the-shopping-cart-items)#### Recuperación de los elementos del carro de la compra

A continuación, agregará código al código subyacente de *ShoppingCart.aspx.cs* para recuperar y rellenar la interfaz de usuario del carro de la compra.

1. En el  **Explorador de soluciones** , haga clic con el botón derecho en la página *ShoppingCart* y, después, haga clic en  **Ver código** . El archivo de código subyacente *ShoppingCart.aspx.cs* se abre en el editor.
2. Reemplace el código existente por el siguiente:

   **C#**
3. ```
   using System;
   using System.Collections.Generic;
   using System.Linq;
   using System.Web;
   using System.Web.UI;
   using System.Web.UI.WebControls;
   using WingtipToys.Models;
   using WingtipToys.Logic;

   namespace WingtipToys
   {
     public partial class ShoppingCart : System.Web.UI.Page
     {
       protected void Page_Load(object sender, EventArgs e)
       {

       }

       public List<CartItem> GetShoppingCartItems()
       {
         ShoppingCartActions actions = new ShoppingCartActions();
         return actions.GetCartItems();
       }
     }
   }
   ```

Como se mencionó anteriormente, el control de datos `GridView` llama al método `GetShoppingCartItems` en el momento adecuado del ciclo de vida de la página y enlaza automáticamente los datos devueltos. El método `GetShoppingCartItems` crea una instancia del objeto de `ShoppingCartActions`. A continuación, el código usa esa instancia para devolver los elementos del carro llamando al método `GetCartItems`.

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#adding-products-to-the-shopping-cart)### Adición de productos al carro de la compra

Cuando se muestra la página *ProductList.aspx* o  *ProductDetails.asp* ,
 el usuario podrá agregar el producto al carro de la compra mediante un
vínculo. Al hacer clic en el vínculo, la aplicación navega a la página
de procesamiento denominada  *AddToCart.aspx* . La página *AddToCart.aspx* llamará al método `AddToCart` en la clase de `ShoppingCart` que agregó anteriormente en este tutorial.

Ahora, agregará un vínculo de **Agregar al carro** tanto a la página *ProductList.aspx* como a  *ProductDetails.aspx* . Este vínculo incluirá el producto `ID` que se recupera de la base de datos.

1. En  **Explorador de soluciones** , busque y abra la página denominada  *ProductList.aspx* .
2. Agregue el marcado resaltado en amarillo a la página *ProductList.aspx* para que la página completa aparezca de la siguiente manera:

   **ASP.NET**
3. ```
   <%@ Page Title="Products" Language="C#" MasterPageFile="~/Site.Master" AutoEventWireup="true" 
            CodeBehind="ProductList.aspx.cs" Inherits="WingtipToys.ProductList" %>
   <asp:Content ID="Content1" ContentPlaceHolderID="MainContent" runat="server">
       <section>
           <div>
               <hgroup>
                   <h2><%: Page.Title %></h2>
               </hgroup>

               <asp:ListView ID="productList" runat="server" 
                   DataKeyNames="ProductID" GroupItemCount="4"
                   ItemType="WingtipToys.Models.Product" SelectMethod="GetProducts">
                   <EmptyDataTemplate>
                       <table runat="server">
                           <tr>
                               <td>No data was returned.</td>
                           </tr>
                       </table>
                   </EmptyDataTemplate>
                   <EmptyItemTemplate>
                       <td runat="server" />
                   </EmptyItemTemplate>
                   <GroupTemplate>
                       <tr id="itemPlaceholderContainer" runat="server">
                           <td id="itemPlaceholder" runat="server"></td>
                       </tr>
                   </GroupTemplate>
                   <ItemTemplate>
                       <td runat="server">
                           <table>
                               <tr>
                                   <td>
                                       <a href="ProductDetails.aspx?productID=<%#:Item.ProductID%>">
                                           <img src="/Catalog/Images/Thumbs/<%#:Item.ImagePath%>"
                                               width="100" height="75" style="border: solid" /></a>
                                   </td>
                               </tr>
                               <tr>
                                   <td>
                                       <a href="ProductDetails.aspx?productID=<%#:Item.ProductID%>">
                                           <span>
                                               <%#:Item.ProductName%>
                                           </span>
                                       </a>
                                       <br />
                                       <span>
                                           <b>Price: </b><%#:String.Format("{0:c}", Item.UnitPrice)%>
                                       </span>
                                       <br />
                                       <a href="/AddToCart.aspx?productID=<%#:Item.ProductID %>">             
                                           <span class="ProductListItem">
                                               <b>Add To Cart<b>
                                           </span>         
                                       </a>
                                   </td>
                               </tr>
                               <tr>
                                   <td> </td>
                               </tr>
                           </table>
                           </p>
                       </td>
                   </ItemTemplate>
                   <LayoutTemplate>
                       <table runat="server" style="width:100%;">
                           <tbody>
                               <tr runat="server">
                                   <td runat="server">
                                       <table id="groupPlaceholderContainer" runat="server" style="width:100%">
                                           <tr id="groupPlaceholder" runat="server"></tr>
                                       </table>
                                   </td>
                               </tr>
                               <tr runat="server">
                                   <td runat="server"></td>
                               </tr>
                               <tr></tr>
                           </tbody>
                       </table>
                   </LayoutTemplate>
               </asp:ListView>
           </div>
       </section>
   </asp:Content>
   ```

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#testing-the-shopping-cart)### Prueba del carro de la compra

Ejecute la aplicación para ver cómo agrega productos al carro de la compra.

1. Presione **F5** para ejecutar la aplicación.

   Después de que el proyecto vuelva a generar la base de datos, el explorador se abrirá y mostrará la página  *Default.aspx* .
2. Seleccione **Cars (Coches)** en el menú de navegación de categorías.

   Se muestra la página *ProductList.aspx* solo con los productos incluidos en la categoría "Coches".
   ![Shopping Cart - Cars](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart/_static/image5.png)
3. Haga clic en el vínculo **Agregar al carro** junto al primer producto que aparece en la lista (el coche descapotable).

   Se muestra la página *ShoppingCart.aspx* con la selección del carro de la compra.
   ![Shopping Cart - Cart](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart/_static/image6.png)
4. Para ver productos adicionales, seleccione **Planos** en el menú de navegación de categorías.
5. Haga clic en el vínculo **Agregar al carro** junto al primer producto de la lista (el coche descapotable).

   La página *ShoppingCart.aspx* se muestra con el elemento adicional.
6. Cierre el explorador.

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#calculating-and-displaying-the-order-total)### Calculo y visualización del total del pedido

Además de agregar productos al carro de la compra, agregará un método `GetTotal` a la clase `ShoppingCart` y se mostrará el importe total del pedido en la página del carro de la compra.

1. En  **Explorador de soluciones** , abra el archivo *ShoppingCartActions.cs* en la carpeta  *Lógica* .
2. Agregue el siguiente método `GetTotal` resaltado en amarillo a la clase de `ShoppingCart` para que la clase se muestre de la siguiente manera:

   **C#**
3. ```
   using System;
   using System.Collections.Generic;
   using System.Linq;
   using System.Web;
   using WingtipToys.Models;

   namespace WingtipToys.Logic
   {
     public class ShoppingCartActions : IDisposable
     {
       public string ShoppingCartId { get; set; }

       private ProductContext _db = new ProductContext();

       public const string CartSessionKey = "CartId";

       public void AddToCart(int id)
       {
         // Retrieve the product from the database.         
         ShoppingCartId = GetCartId();

         var cartItem = _db.ShoppingCartItems.SingleOrDefault(
             c => c.CartId == ShoppingCartId
             && c.ProductId == id);
         if (cartItem == null)
         {
           // Create a new cart item if no cart item exists.               
           cartItem = new CartItem
           {
             ItemId = Guid.NewGuid().ToString(),
             ProductId = id,
             CartId = ShoppingCartId,
             Product = _db.Products.SingleOrDefault(
              p => p.ProductID == id),
             Quantity = 1,
             DateCreated = DateTime.Now
           };

           _db.ShoppingCartItems.Add(cartItem);
         }
         else
         {
           // If the item does exist in the cart,                
           // then add one to the quantity.               
           cartItem.Quantity++;
         }
         _db.SaveChanges();
       }

       public void Dispose()
       {
         if (_db != null)
         {
           _db.Dispose();
           _db = null;
         }
       }

       public string GetCartId()
       {
         if (HttpContext.Current.Session[CartSessionKey] == null)
         {
           if (!string.IsNullOrWhiteSpace(HttpContext.Current.User.Identity.Name))
           {
             HttpContext.Current.Session[CartSessionKey] = HttpContext.Current.User.Identity.Name;
           }
           else
           {
             // Generate a new random GUID using System.Guid class.   
             Guid tempCartId = Guid.NewGuid();
             HttpContext.Current.Session[CartSessionKey] = tempCartId.ToString();
           }
         }
         return HttpContext.Current.Session[CartSessionKey].ToString();
       }

       public List<CartItem> GetCartItems()
       {
         ShoppingCartId = GetCartId();

         return _db.ShoppingCartItems.Where(
             c => c.CartId == ShoppingCartId).ToList();
       }

       public decimal GetTotal()
       {
         ShoppingCartId = GetCartId();
         // Multiply product price by quantity of that product to get      
         // the current price for each of those products in the cart.  
         // Sum all product price totals to get the cart total.   
         decimal? total = decimal.Zero;
         total = (decimal?)(from cartItems in _db.ShoppingCartItems
                            where cartItems.CartId == ShoppingCartId
                            select (int?)cartItems.Quantity *
                            cartItems.Product.UnitPrice).Sum();
         return total ?? decimal.Zero;
       }
     }
   }
   ```

En primer lugar, el método `GetTotal` obtiene el id. del
carro de la compra del usuario. A continuación, el método obtiene el
total del carro multiplicando el precio del producto por la cantidad de
producto para cada producto incluido en el carro.

 Nota:

El código anterior usa el tipo que acepta valores NULL "`int?`".
 Los tipos que aceptan valores NULL pueden representar todos los valores
 de un tipo subyacente y también como un valor null. Para obtener más
información, consulte [Uso de tipos que aceptan valores NULL](https://msdn.microsoft.com/library/2cf62fcy(v=vs.110).aspx).

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#modify-the-shopping-cart-display)### Modificación de la presentación del carro de la compra

A continuación, modificará el código de la página*ShoppingCart.aspx* para llamar al método de `GetTotal` y mostrar ese total en la página *ShoppingCart.aspx* cuando se cargue la página.

1. En el  **Explorador de soluciones** , haga clic con el botón derecho en la página *ShoppingCart.aspx* y seleccione  **Ver código** .
2. En el archivo  *ShoppingCart.aspx.cs* , actualice el controlador de `Page_Load` agregando el código siguiente resaltado en amarillo:

   **C#**
3. ```
   using System;
   using System.Collections.Generic;
   using System.Linq;
   using System.Web;
   using System.Web.UI;
   using System.Web.UI.WebControls;
   using WingtipToys.Models;
   using WingtipToys.Logic;

   namespace WingtipToys
   {
     public partial class ShoppingCart : System.Web.UI.Page
     {
       protected void Page_Load(object sender, EventArgs e)
       {
         using (ShoppingCartActions usersShoppingCart = new ShoppingCartActions())
         {
           decimal cartTotal = 0;
           cartTotal = usersShoppingCart.GetTotal();
           if (cartTotal > 0)
           {
             // Display Total.
             lblTotal.Text = String.Format("{0:c}", cartTotal);
           }
           else
           {
             LabelTotalText.Text = "";
             lblTotal.Text = "";
             ShoppingCartTitle.InnerText = "Shopping Cart is Empty";
           }
         }
       }

       public List<CartItem> GetShoppingCartItems()
       {
         ShoppingCartActions actions = new ShoppingCartActions();
         return actions.GetCartItems();
       }
     }
   }
   ```

Cuando se carga la página  *ShoppingCart.aspx* , se carga el objeto del carro de la compra y, a continuación, se recupera el total del carro de la compra llamando al método `GetTotal` de la clase de `ShoppingCart`. Si el carro de la compra está vacío, se muestra un mensaje a ese efecto.

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#testing-the-shopping-cart-total)### Prueba del total del carro de la compra

Ejecute la aplicación ahora para ver no solo cómo puede agregar un
producto al carro de la compra, sino también para consultar el total del
 carro de la compra.

1. Presione **F5** para ejecutar la aplicación.

   El explorador se abrirá y mostrará la página *Default.aspx* .
2. Seleccione **Cars (Coches)** en el menú de navegación de categorías.
3. Haga clic en el vínculo **Agregar al carro** junto al primer producto de la lista.

   La página *ShoppingCart.aspx* se muestra con el total del pedido.
   ![Shopping Cart - Cart Total](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart/_static/image7.png)
4. Agregue otros productos (por ejemplo, un plano) al carro.
5. La página *ShoppingCart.aspx* se muestra con un total actualizado para todos los productos que ha agregado.
   ![Shopping Cart - Multiple Products](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart/_static/image8.png)
6. Cierre la ventana del explorador para detener la aplicación en ejecución.

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#adding-update-and-checkout-buttons-to-the-shopping-cart)### Adición de botones de actualización y finalización de la compra al carro de la compra

Para permitir que los usuarios modifiquen el carro de la compra, agregará un botón **Actualizar** y un botón **Finalización de la compra** a la página del carro de la compra. El botón **Finalización de la compra** no se usa hasta más adelante en esta serie de tutoriales.

1. En el  **Explorador de soluciones** , abra la página *ShoppingCart.aspx* en la raíz del proyecto de aplicación web.
2. Para agregar el botón **Actualizar** y el botón **Finalización de la compra** a la página  *ShoppingCart.aspx* , agregue el marcado resaltado en amarillo al marcado existente, como se muestra en el código siguiente:

   **ASP.NET**
3. ```
   <%@ Page Title="" Language="C#" MasterPageFile="~/Site.Master" AutoEventWireup="true" CodeBehind="ShoppingCart.aspx.cs" Inherits="WingtipToys.ShoppingCart" %>
   <asp:Content ID="Content1" ContentPlaceHolderID="MainContent" runat="server">
       <div id="ShoppingCartTitle" runat="server" class="ContentHead"><h1>Shopping Cart</h1></div>
       <asp:GridView ID="CartList" runat="server" AutoGenerateColumns="False" ShowFooter="True" GridLines="Vertical" CellPadding="4"
           ItemType="WingtipToys.Models.CartItem" SelectMethod="GetShoppingCartItems"  
           CssClass="table table-striped table-bordered" >   
           <Columns>
           <asp:BoundField DataField="ProductID" HeaderText="ID" SortExpression="ProductID" />      
           <asp:BoundField DataField="Product.ProductName" HeaderText="Name" />      
           <asp:BoundField DataField="Product.UnitPrice" HeaderText="Price (each)" DataFormatString="{0:c}"/>   
           <asp:TemplateField   HeaderText="Quantity">          
                   <ItemTemplate>
                       <asp:TextBox ID="PurchaseQuantity" Width="40" runat="server" Text="<%#: Item.Quantity %>"></asp:TextBox> 
                   </ItemTemplate>      
           </asp:TemplateField>  
           <asp:TemplateField HeaderText="Item Total">          
                   <ItemTemplate>
                       <%#: String.Format("{0:c}", ((Convert.ToDouble(Item.Quantity)) *  Convert.ToDouble(Item.Product.UnitPrice)))%>
                   </ItemTemplate>      
           </asp:TemplateField> 
           <asp:TemplateField HeaderText="Remove Item">          
                   <ItemTemplate>
                       <asp:CheckBox id="Remove" runat="server"></asp:CheckBox>
                   </ItemTemplate>      
           </asp:TemplateField>  
           </Columns>  
       </asp:GridView>
       <div>
           <p></p>
           <strong>
               <asp:Label ID="LabelTotalText" runat="server" Text="Order Total: "></asp:Label>
               <asp:Label ID="lblTotal" runat="server" EnableViewState="false"></asp:Label>
           </strong> 
       </div>
     <br />
       <table> 
       <tr>
         <td>
           <asp:Button ID="UpdateBtn" runat="server" Text="Update" OnClick="UpdateBtn_Click" />
         </td>
         <td>
           <!--Checkout Placeholder -->
         </td>
       </tr>
       </table>
   </asp:Content>
   ```

Cuando el usuario hace clic en el botón  **Actualizar** , se llamará al controlador de eventos `UpdateBtn_Click`. Este controlador llamará al código que va a agregar en el paso siguiente.

A continuación, puede actualizar el código incluido en el archivo *ShoppingCart.aspx.cs* para recorrer en bucle los elementos del carro y llamar a los métodos `RemoveItem` y `UpdateItem`.

1. En el  **Explorador de soluciones** , abra el archivo *ShoppingCart.aspx.cs* en la raíz del proyecto de aplicación web.
2. Agregue las secciones siguientes del código resaltadas en amarillo al archivo  *ShoppingCart.aspx.cs* :

   **C#**
3. ```
   using System;
   using System.Collections.Generic;
   using System.Linq;
   using System.Web;
   using System.Web.UI;
   using System.Web.UI.WebControls;
   using WingtipToys.Models;
   using WingtipToys.Logic;
   using System.Collections.Specialized;
   using System.Collections;
   using System.Web.ModelBinding;

   namespace WingtipToys
   {
     public partial class ShoppingCart : System.Web.UI.Page
     {
       protected void Page_Load(object sender, EventArgs e)
       {
         using (ShoppingCartActions usersShoppingCart = new ShoppingCartActions())
         {
           decimal cartTotal = 0;
           cartTotal = usersShoppingCart.GetTotal();
           if (cartTotal > 0)
           {
             // Display Total.
             lblTotal.Text = String.Format("{0:c}", cartTotal);
           }
           else
           {
             LabelTotalText.Text = "";
             lblTotal.Text = "";
             ShoppingCartTitle.InnerText = "Shopping Cart is Empty";
             UpdateBtn.Visible = false;
           }
         }
       }

       public List<CartItem> GetShoppingCartItems()
       {
         ShoppingCartActions actions = new ShoppingCartActions();
         return actions.GetCartItems();
       }

       public List<CartItem> UpdateCartItems()
       {
         using (ShoppingCartActions usersShoppingCart = new ShoppingCartActions())
         {
           String cartId = usersShoppingCart.GetCartId();

           ShoppingCartActions.ShoppingCartUpdates[] cartUpdates = new ShoppingCartActions.ShoppingCartUpdates[CartList.Rows.Count];
           for (int i = 0; i < CartList.Rows.Count; i++)
           {
             IOrderedDictionary rowValues = new OrderedDictionary();
             rowValues = GetValues(CartList.Rows[i]);
             cartUpdates[i].ProductId = Convert.ToInt32(rowValues["ProductID"]);

             CheckBox cbRemove = new CheckBox();
             cbRemove = (CheckBox)CartList.Rows[i].FindControl("Remove");
             cartUpdates[i].RemoveItem = cbRemove.Checked;

             TextBox quantityTextBox = new TextBox();
             quantityTextBox = (TextBox)CartList.Rows[i].FindControl("PurchaseQuantity");
             cartUpdates[i].PurchaseQuantity = Convert.ToInt16(quantityTextBox.Text.ToString());
           }
           usersShoppingCart.UpdateShoppingCartDatabase(cartId, cartUpdates);
           CartList.DataBind();
           lblTotal.Text = String.Format("{0:c}", usersShoppingCart.GetTotal());
           return usersShoppingCart.GetCartItems();
         }
       }

       public static IOrderedDictionary GetValues(GridViewRow row)
       {
         IOrderedDictionary values = new OrderedDictionary();
         foreach (DataControlFieldCell cell in row.Cells)
         {
           if (cell.Visible)
           {
             // Extract values from the cell.
             cell.ContainingField.ExtractValuesFromCell(values, cell, row.RowState, true);
           }
         }
         return values;
       }

       protected void UpdateBtn_Click(object sender, EventArgs e)
       {
         UpdateCartItems();
       }
     }
   }
   ```

Cuando el usuario hace clic en el botón **Actualizar** de la página  *ShoppingCart.aspx* ,
 se llama al método UpdateCartItems. El método UpdateCartItems obtiene
los valores actualizados de cada elemento del carro de la compra. A
continuación, el método UpdateCartItems llama al método `UpdateShoppingCartDatabase`
 (agregado y explicado en el paso siguiente) para agregar o quitar
elementos del carro de la compra. Una vez que se actualice la base de
datos para que refleje las actualizaciones del carro de la compra, el
control **GridView** se actualiza en la página del carro de la compra llamando al método `DataBind` del  **GridView** .
 Además, el importe total del pedido en la página del carro de la compra
 se actualiza para reflejar la lista actualizada de elementos.

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#updating-and-removing-shopping-cart-items)### Actualización y eliminación de elementos del carro de la compra

En la página  *ShoppingCart.aspx* , puede ver que se han
agregado controles para actualizar la cantidad de un elemento y quitar
otro. Ahora, agregue el código que hará que estos controles funcionen.

1. En  **Explorador de soluciones** , abra el archivo *ShoppingCartActions.cs* en la carpeta  *Lógica* .
2. Agregue el código siguiente resaltado en amarillo al archivo de clase  *ShoppingCartActions.cs* :

   **C#**
3. ```
   using System;
   using System.Collections.Generic;
   using System.Linq;
   using System.Web;
   using WingtipToys.Models;

   namespace WingtipToys.Logic
   {
     public class ShoppingCartActions : IDisposable
     {
       public string ShoppingCartId { get; set; }

       private ProductContext _db = new ProductContext();

       public const string CartSessionKey = "CartId";

       public void AddToCart(int id)
       {
         // Retrieve the product from the database.         
         ShoppingCartId = GetCartId();

         var cartItem = _db.ShoppingCartItems.SingleOrDefault(
             c => c.CartId == ShoppingCartId
             && c.ProductId == id);
         if (cartItem == null)
         {
           // Create a new cart item if no cart item exists.               
           cartItem = new CartItem
           {
             ItemId = Guid.NewGuid().ToString(),
             ProductId = id,
             CartId = ShoppingCartId,
             Product = _db.Products.SingleOrDefault(
              p => p.ProductID == id),
             Quantity = 1,
             DateCreated = DateTime.Now
           };

           _db.ShoppingCartItems.Add(cartItem);
         }
         else
         {
           // If the item does exist in the cart,                
           // then add one to the quantity.               
           cartItem.Quantity++;
         }
         _db.SaveChanges();
       }

       public void Dispose()
       {
         if (_db != null)
         {
           _db.Dispose();
           _db = null;
         }
       }

       public string GetCartId()
       {
         if (HttpContext.Current.Session[CartSessionKey] == null)
         {
           if (!string.IsNullOrWhiteSpace(HttpContext.Current.User.Identity.Name))
           {
             HttpContext.Current.Session[CartSessionKey] = HttpContext.Current.User.Identity.Name;
           }
           else
           {
             // Generate a new random GUID using System.Guid class.   
             Guid tempCartId = Guid.NewGuid();
             HttpContext.Current.Session[CartSessionKey] = tempCartId.ToString();
           }
         }
         return HttpContext.Current.Session[CartSessionKey].ToString();
       }

       public List<CartItem> GetCartItems()
       {
         ShoppingCartId = GetCartId();

         return _db.ShoppingCartItems.Where(
             c => c.CartId == ShoppingCartId).ToList();
       }

       public decimal GetTotal()
       {
         ShoppingCartId = GetCartId();
         // Multiply product price by quantity of that product to get      
         // the current price for each of those products in the cart.  
         // Sum all product price totals to get the cart total.   
         decimal? total = decimal.Zero;
         total = (decimal?)(from cartItems in _db.ShoppingCartItems
                            where cartItems.CartId == ShoppingCartId
                            select (int?)cartItems.Quantity *
                            cartItems.Product.UnitPrice).Sum();
         return total ?? decimal.Zero;
       }

       public ShoppingCartActions GetCart(HttpContext context)
       {
         using (var cart = new ShoppingCartActions())
         {
           cart.ShoppingCartId = cart.GetCartId();
           return cart;
         }
       }

       public void UpdateShoppingCartDatabase(String cartId, ShoppingCartUpdates[] CartItemUpdates)
       {
         using (var db = new WingtipToys.Models.ProductContext())
         {
           try
           {
             int CartItemCount = CartItemUpdates.Count();
             List<CartItem> myCart = GetCartItems();
             foreach (var cartItem in myCart)
             {
               // Iterate through all rows within shopping cart list
               for (int i = 0; i < CartItemCount; i++)
               {
                 if (cartItem.Product.ProductID == CartItemUpdates[i].ProductId)
                 {
                   if (CartItemUpdates[i].PurchaseQuantity < 1 || CartItemUpdates[i].RemoveItem == true)
                   {
                     RemoveItem(cartId, cartItem.ProductId);
                   }
                   else
                   {
                     UpdateItem(cartId, cartItem.ProductId, CartItemUpdates[i].PurchaseQuantity);
                   }
                 }
               }
             }
           }
           catch (Exception exp)
           {
             throw new Exception("ERROR: Unable to Update Cart Database - " + exp.Message.ToString(), exp);
           }
         }
       }

       public void RemoveItem(string removeCartID, int removeProductID)
       {
         using (var _db = new WingtipToys.Models.ProductContext())
         {
           try
           {
             var myItem = (from c in _db.ShoppingCartItems where c.CartId == removeCartID && c.Product.ProductID == removeProductID select c).FirstOrDefault();
             if (myItem != null)
             {
               // Remove Item.
               _db.ShoppingCartItems.Remove(myItem);
               _db.SaveChanges();
             }
           }
           catch (Exception exp)
           {
             throw new Exception("ERROR: Unable to Remove Cart Item - " + exp.Message.ToString(), exp);
           }
         }
       }

       public void UpdateItem(string updateCartID, int updateProductID, int quantity)
       {
         using (var _db = new WingtipToys.Models.ProductContext())
         {
           try
           {
             var myItem = (from c in _db.ShoppingCartItems where c.CartId == updateCartID && c.Product.ProductID == updateProductID select c).FirstOrDefault();
             if (myItem != null)
             {
               myItem.Quantity = quantity;
               _db.SaveChanges();
             }
           }
           catch (Exception exp)
           {
             throw new Exception("ERROR: Unable to Update Cart Item - " + exp.Message.ToString(), exp);
           }
         }
       }

       public void EmptyCart()
       {
         ShoppingCartId = GetCartId();
         var cartItems = _db.ShoppingCartItems.Where(
             c => c.CartId == ShoppingCartId);
         foreach (var cartItem in cartItems)
         {
           _db.ShoppingCartItems.Remove(cartItem);
         }
         // Save changes.           
         _db.SaveChanges();
       }

       public int GetCount()
       {
         ShoppingCartId = GetCartId();

         // Get the count of each item in the cart and sum them up        
         int? count = (from cartItems in _db.ShoppingCartItems
                       where cartItems.CartId == ShoppingCartId
                       select (int?)cartItems.Quantity).Sum();
         // Return 0 if all entries are null       
         return count ?? 0;
       }

       public struct ShoppingCartUpdates
       {
         public int ProductId;
         public int PurchaseQuantity;
         public bool RemoveItem;
       }
     }
   }
   ```

El método `UpdateShoppingCartDatabase`, al que se llama desde el método `UpdateCartItems` de la página  *ShoppingCart.aspx.cs* , contiene la lógica para actualizar o quitar elementos del carro de la compra. El método `UpdateShoppingCartDatabase`
 recorre en iteración todas las filas de la lista de carros de la
compra. Si se ha marcado un elemento del carro de la compra para
quitarlo o la cantidad es inferior a uno, se llama al método `RemoveItem`. De lo contrario, se comprueba si hay actualizaciones del elemento del carro de la compra cuando se llama al método `UpdateItem`. Después de quitar o actualizar el elemento del carro de la compra, se guardan los cambios de la base de datos.

La estructura de `ShoppingCartUpdates` se utiliza para almacenar todos los elementos del carro de la compra. El método `UpdateShoppingCartDatabase` usa la estructura `ShoppingCartUpdates` para determinar si alguno de los elementos debe actualizarse o quitarse.

En el siguiente tutorial, usará el método `EmptyCart` para borrar el carro de la compra después de comprar productos. Pero de momento, usará el método `GetCount` que acaba de agregar al archivo *ShoppingCartActions.cs* para determinar cuántos elementos hay en el carro de la compra.

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#adding-a-shopping-cart-counter)### Adición de un contador al carro de la compra

Para permitir que el usuario vea el número total de elementos en el carro de la compra, agregará un contador a la página  *Site.Master* . Este contador también actuará como un vínculo al carro de la compra.

1. En el  **Explorador de soluciones** , abra la página  *Site.Master* .
2. Modifique el marcado agregando a la sección de navegación el
   vínculo del contador del carro de la compra tal y como se muestra en
   amarillo para que aparezca como se indica a continuación:

   **HTML**

* ```
  <ul class="nav navbar-nav">
        <li><a runat="server" href="~/">Home</a></li>
        <li><a runat="server" href="~/About">About</a></li>
        <li><a runat="server" href="~/Contact">Contact</a></li>
        <li><a runat="server" href="~/ProductList">Products</a></li>
        <li><a runat="server" href="~/ShoppingCart" ID="cartCount"> </a></li>
    </ul>
  ```
* A continuación, actualice el código subyacente del archivo *Site.Master.cs* agregando el código resaltado en amarillo de la siguiente manera:

  **C#**

1. ```
   using System;
   using System.Collections.Generic;
   using System.Security.Claims;
   using System.Security.Principal;
   using System.Web;
   using System.Web.Security;
   using System.Web.UI;
   using System.Web.UI.WebControls;
   using System.Linq;
   using WingtipToys.Models;
   using WingtipToys.Logic;

   namespace WingtipToys
   {
       public partial class SiteMaster : MasterPage
       {
           private const string AntiXsrfTokenKey = "__AntiXsrfToken";
           private const string AntiXsrfUserNameKey = "__AntiXsrfUserName";
           private string _antiXsrfTokenValue;

           protected void Page_Init(object sender, EventArgs e)
           {
               // The code below helps to protect against XSRF attacks
               var requestCookie = Request.Cookies[AntiXsrfTokenKey];
               Guid requestCookieGuidValue;
               if (requestCookie != null && Guid.TryParse(requestCookie.Value, out requestCookieGuidValue))
               {
                   // Use the Anti-XSRF token from the cookie
                   _antiXsrfTokenValue = requestCookie.Value;
                   Page.ViewStateUserKey = _antiXsrfTokenValue;
               }
               else
               {
                   // Generate a new Anti-XSRF token and save to the cookie
                   _antiXsrfTokenValue = Guid.NewGuid().ToString("N");
                   Page.ViewStateUserKey = _antiXsrfTokenValue;

                   var responseCookie = new HttpCookie(AntiXsrfTokenKey)
                   {
                       HttpOnly = true,
                       Value = _antiXsrfTokenValue
                   };
                   if (FormsAuthentication.RequireSSL && Request.IsSecureConnection)
                   {
                       responseCookie.Secure = true;
                   }
                   Response.Cookies.Set(responseCookie);
               }

               Page.PreLoad += master_Page_PreLoad;
           }

           protected void master_Page_PreLoad(object sender, EventArgs e)
           {
               if (!IsPostBack)
               {
                   // Set Anti-XSRF token
                   ViewState[AntiXsrfTokenKey] = Page.ViewStateUserKey;
                   ViewState[AntiXsrfUserNameKey] = Context.User.Identity.Name ?? String.Empty;
               }
               else
               {
                   // Validate the Anti-XSRF token
                   if ((string)ViewState[AntiXsrfTokenKey] != _antiXsrfTokenValue
                       || (string)ViewState[AntiXsrfUserNameKey] != (Context.User.Identity.Name ?? String.Empty))
                   {
                       throw new InvalidOperationException("Validation of Anti-XSRF token failed.");
                   }
               }
           }

           protected void Page_Load(object sender, EventArgs e)
           {

           }

           protected void Page_PreRender(object sender, EventArgs e)
           {
             using (ShoppingCartActions usersShoppingCart = new ShoppingCartActions())
             {
               string cartStr = string.Format("Cart ({0})", usersShoppingCart.GetCount());
               cartCount.InnerText = cartStr;
             }
           }

           public IQueryable<Category> GetCategories()
           {
             var _db = new WingtipToys.Models.ProductContext();
             IQueryable<Category> query = _db.Categories;
             return query;
           }

           protected void Unnamed_LoggingOut(object sender, LoginCancelEventArgs e)
           {
               Context.GetOwinContext().Authentication.SignOut();
           }
       }
   }
   ```

Antes de que la página se represente como HTML, se genera el evento `Page_PreRender`. En el controlador `Page_PreRender`, el recuento total del carro de la compra se determina llamando al método `GetCount`. El valor devuelto se agrega al intervalo de `cartCount` incluido en el marcado de la página  *Site.Master* . Las etiquetas de `<span>`
 permiten representar correctamente los elementos internos. Cuando se
muestra cualquier página del sitio, se mostrará el total del carro de la
 compra. El usuario también puede hacer clic en el total del carro de la
 compra para que se muestre el propio carro de la compra.

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#testing-the-completed-shopping-cart)## Prueba del carro de la compra completado

Ahora puede ejecutar la aplicación para ver cómo agregar, eliminar y
actualizar elementos en el carro de la compra. El total del carro de la
compra reflejará el coste total de todos los elementos que se incluyen
en él.

1. Presione **F5** para ejecutar la aplicación.

   El explorador se abre y muestra la página  *Default.aspx* .
2. Seleccione **Cars (Coches)** en el menú de navegación de categorías.
3. Haga clic en el vínculo **Agregar al carro** junto al primer producto de la lista.

   La página *ShoppingCart.aspx* se muestra con el total del pedido.
4. Seleccione **Planes** en el menú de navegación de categorías.
5. Haga clic en el vínculo **Agregar al carro** junto al primer producto de la lista.
6. Establezca la cantidad del primer elemento del carro de la compra en 3 y active la casilla **Quitar elemento** del segundo elemento.[]()
7. Haga clic en el botón **Actualizar** para actualizar la página del carro de la compra y muestre el nuevo total del pedido.
   ![Shopping Cart - Cart Update](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart/_static/image9.png)

[](https://learn.microsoft.com/es-es/aspnet/web-forms/overview/getting-started/getting-started-with-aspnet-45-web-forms/shopping-cart#summary)## Resumen

En este tutorial, ha creado un carro de la compra para la aplicación
de ejemplo Wingtip Toys de Web Forms. Durante este tutorial ha usado
Entity Framework Code First, anotaciones de datos, controles de datos
fuertemente tipados y enlace de modelos.

El carro de la compra admite la adición, eliminación y actualización
de elementos que el usuario ha seleccionado para su compra. Además de
implementar la funcionalidad del carro de la compra, ha aprendido a
mostrar elementos de carro de la compra en un control **GridView** y calcular el total del pedido.

Para comprender cómo funciona la funcionalidad descrita en una
aplicación empresarial real, puede ver el ejemplo del carro de la compra
 eCommerce de código abierto basado en [nopCommerce](https://github.com/nopSolutions/nopCommerce) - ASP.NET. Originalmente, se compiló en Web Forms y, a lo largo de los años, se trasladó a MVC y ahora a ASP.NET Core.
