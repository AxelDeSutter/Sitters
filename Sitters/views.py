'''
Created on Dec 16, 2019

@author: groupe13
'''
from django.shortcuts import render, redirect

from django.utils.html import escape

from Sitters.models import User, Disponibilities, Message, Comment, Child, Favorite, Chat, Report
from django.contrib.sessions.models import Session

def Home(request):
    if "User" in request.session:
        # On récupère toutes les informations de l'utilisateur connecté
        SessionUser = User.objects.filter(Email=request.session["User"])
        
        if SessionUser[0].Banned:
            return redirect('/Logout')
        # On cherche toutes les disponibilités de l'utilisateur connecté
        Query = Disponibilities.objects.filter(SitterId=SessionUser[0].pk,Reserved=False).order_by('Date')
        # On vérifie qu'il n'y a aucun message pour l'utilisateur connecté
        Messages = Message.objects.filter(Target=SessionUser[0].pk)
        # On récupère les chats
        Chats = Chat.objects.filter(Sender=SessionUser[0].pk)|Chat.objects.filter(Receiver=SessionUser[0].pk)
        
        ChattingUsers = []
        for I in Chats:
            if I.Sender == SessionUser[0].pk:
                if I.Receiver not in ChattingUsers:
                    ChattingUsers.append(I.Receiver)
            else:
                if I.Sender not in ChattingUsers:
                    ChattingUsers.append(I.Sender)
        
        ChattingUsers = User.objects.filter(pk__in=ChattingUsers)
            
        # Si l'utilisateur connecté n'est pas un Parent
        if request.session["Status"] != "Parent":
            # Si c'est un parent ET un babysitter
            if request.session["Status"] == "Both":
                # On récupère tous les utilisateurs favoris de la session en excluant la session elle même, pour éviter la redondance
                Favorites = Favorite.objects.filter(User=SessionUser[0].pk).exclude(FavoriteUser=SessionUser[0].pk)
                # On créée un tableau avec les pk des utilisateurs favoris 
                FavoriteUsers = []
                for Fav in Favorites:
                    FavoriteUsers.append(Fav.FavoriteUser)
                # On récupère toutes les disponibilités des utilisateurs à l'intérieur de la liste FavoriteUsers
                FavoriteDisponibilities = Disponibilities.objects.filter(SitterId__in=FavoriteUsers,Reserved=False).order_by('Date')
                # On ajoute à tous les objets Disponibilities récupérés un attribut "UserId" et "Name"
                for FavDispo in FavoriteDisponibilities: 
                    setattr(FavDispo, 'UserId', User.objects.filter(pk=FavDispo.SitterId)[0].pk)
                    setattr(FavDispo, 'Name', User.objects.filter(pk=FavDispo.SitterId)[0].Firstname + " " + User.objects.filter(pk=FavDispo.SitterId)[0].Lastname)
                
                Variables = {"SessionUser": SessionUser[0], "Chats": ChattingUsers,"Profit": Profit(SessionUser[0].pk),"Disponibilities": Query, "Messages": Messages, "FavoriteDisponibilities": FavoriteDisponibilities}
                return render(request, "Home.html", Variables)
            else:
                Variables = {"SessionUser": SessionUser[0], "Chats": ChattingUsers, "Profit": Profit(SessionUser[0].pk), "Disponibilities": Query, "Messages": Messages}
                return render(request, "Home.html", Variables)
        else:
            Favorites = Favorite.objects.filter(User=SessionUser[0].pk).exclude(FavoriteUser=SessionUser[0].pk)
            FavoriteUsers = []
            for Fav in Favorites:
                FavoriteUsers.append(Fav.FavoriteUser)
            FavoriteDisponibilities = Disponibilities.objects.filter(SitterId__in=FavoriteUsers,Reserved=False)
            
            for FavDispo in FavoriteDisponibilities: 
                setattr(FavDispo, 'UserId', User.objects.filter(pk=FavDispo.SitterId)[0].pk)
                setattr(FavDispo, 'Name', User.objects.filter(pk=FavDispo.SitterId)[0].Firstname + " " + User.objects.filter(pk=FavDispo.SitterId)[0].Lastname)
                    
            Variables = {"Status": request.session["Status"], "SessionUser": SessionUser[0], "Chats": ChattingUsers, "Profit": Profit(SessionUser[0].pk), "FavoriteDisponibilities": FavoriteDisponibilities}
            return render(request, "Home.html", Variables)
    else:
        return redirect("/Login")
    
def Register(request):
    # On vérifie que toutes les input ne sont pas vides
    if len(request.GET) > 0:
        # On vérifie que tous les champs obligatoires sont remplis
        if request.GET["Firstname"] != "" and request.GET["Lastname"] != "" and request.GET["Email"] != "" and request.GET["PasswordOne"] != "" and request.GET["PasswordTwo"] != "" and request.GET["City"] != "" and request.GET["Street"] != "" and request.GET["Infos"] != "":
            #On vérifie que les deux mots de passe coïncident
            if request.GET["PasswordOne"] == request.GET["PasswordTwo"]:
                # On créée l'utilisateur
                # escape(TEXT) permet d'échapper les caractères spéciaux pour éviter qu'un pirate n'entre du SQL dans les input
                # On cherche dans la base de données un User dont l'adresse mail est request.GET
                Query = User.objects.filter(Email=escape(request.GET["Email"]))
                # Si le résultat de la recherche est nul, donc si un utilisateur n'a jamais utilisé cette adresse
                if len(Query) == 0:
                    NewUser = User(
                        Email=escape(request.GET["Email"]),
                        Password=escape(request.GET["PasswordOne"]),
                        Firstname=escape(request.GET["Firstname"]),
                        Lastname=escape(request.GET["Lastname"]),
                        City=escape(request.GET["City"]),
                        Street=escape(request.GET["Street"]),
                        Status=escape(request.GET["Status"]),
                        Infos=escape(request.GET["Infos"]),
                    )
                    
                    NewUser.save()
                    request.session["User"] = escape(request.GET["Email"])
                    request.session["Status"] = escape(request.GET["Status"])
                    # Si le compte créé est un compte parent:
                    if request.GET["Status"] == "Parent":
                        # On propose d'ajouter un enfant
                        return redirect('/Child')
                    # Autrement, donc si il s'agit d'un compte Sitter ou Parent et Sitter
                    else:
                        # On demande l'âge et les tarifs du sitter
                        return redirect('/SitterInfos')
                else:
                    Variables = {"Error": "Cette adresse e-mail est déjà utilisée..."}
                    return render(request, "Register.html", Variables)
            else:
                Variables = {"Error": "Les deux mots de passe ne sont pas identiques..."}
                return render(request, "Register.html", Variables)
        else:
            Variables = {"Error": "Merci de compléter tous les champs obligatoires..."}
            return render(request, "Register.html", Variables)
    else:
        return render(request, "Register.html")
       
def SitterInfos(request):
    if "User" in request.session:
        SessionUser = User.objects.filter(Email=request.session["User"])
        if len(request.GET) > 0:
            # On modifie l'age et les tarfis du sitter
            Query = User.objects.filter(Email=request.session["User"]).update(Age=int(escape(request.GET["Age"])),Price=float(escape(request.GET["Price"])),Infos=escape(request.GET["Infos"]))
            return redirect('/')
        else:
            # On charge les anciennes valeurs de l'age et des tarifs à modifier
            Query = User.objects.filter(Email=request.session["User"])
            return render(request, "SitterInfos.html", {"Age": Query[0].Age, "Price": Query[0].Price, "Infos": Query[0].Infos, "SessionUser": SessionUser[0]})
    else:
        return redirect('/Login')  
    
def AddChild(request):
    if "User" in request.session:
        # On récupère toutes les informations sur l'utilisateur connecté
        SessionUser = User.objects.filter(Email=request.session["User"])
        # Si l'utilisateur est un parent ou un both
        if request.session["Status"] != "Sitter":
            # On récupère tous les enfants enregistrés
            Childs = Child.objects.filter(Parent=User.objects.filter(Email=request.session["User"]))
            if len(request.GET) > 0:
                if request.GET["Name"] != "" and request.GET["Age"] != "" and request.GET["Infos"]:
                   # On enregistre le nouvel enfant 
                    NewChild = Child(
                       Name=escape(request.GET["Name"]),
                       Age=int(escape(request.GET["Age"])),
                       Parent=escape(request.GET["Parent"]),
                       Sex=escape(request.GET["Sex"]),
                       Infos=escape(request.GET["Infos"])
                    )
                    NewChild.save()
                    return render(request, "Child.html", {"SessionUser": SessionUser[0], "Success": "Votre enfant a été inscrit avec succès !","Parent": User.objects.filter(Email=request.session["User"])[0].pk, "Childs": Childs})
                else:
                    return render(request, "Child.html", {"SessionUser": SessionUser[0], "Error": "Merci de compléter tous les champs...","Parent": User.objects.filter(Email=request.session["User"])[0].pk, "Childs": Childs})
            else:
                return render(request, 'Child.html', {"SessionUser": SessionUser[0], "Parent": User.objects.filter(Email=request.session["User"])[0].pk, "Childs": Childs})
        else:
            return redirect('/')
    else:
        return redirect('/')
    
def Login(request):
    if len(request.GET) > 0:
        # On vérifie qu'il existe bien un utilisateur avec cet email et ce mot de passe
        Query = User.objects.filter(Email=escape(request.GET["Email"]),Password=escape(request.GET["Password"]))
        if len(Query) > 0:
            # On créée une session "User" avec l'adresse e-mail pour pouvoir vérifier que l'utilisateur est connecté.
            if not Query[0].Banned:
                request.session["User"] = escape(request.GET["Email"])  
                request.session["Status"] = Query[0].Status 
                return redirect('/')
            else:
                return render(request, "Login.html", {"Error": "Désolé, il semblerait que votre compte ait été banni.<br/>Si vous pensez qu'il s'agit d'une erreur, vous pouvez contacter Sitters à l'adresse <b>help@sitters.com</b>"})
        else:
            return render(request, "Login.html", {"Error": "Cet utilisateur n'existe pas..."})
    else:
        return render(request, "Login.html")
    
def Logout(request):
    # Le code va essayer de supprimer la variable de session
    try:
        del request.session['User']
    # En cas d'erreur "KeyError", donc si la session n'existait pas, le code va "passer" à la suite
    except KeyError:
        pass
    # On redirige vers la page d'accueil
    return redirect('/')

def AddDisponibility(request):
    if "User" in request.session:
        SessionUser = User.objects.filter(Email=request.session["User"])
        if len(request.GET) > 0 and request.GET["Day"] != "" and request.GET["Month"] != "" and request.GET["Year"] != "":
            if 0 < int(request.GET["Day"]) <= 31:
                if 0 < int(request.GET["Month"]) <= 12:
                    if 2019 <= int(request.GET["Year"]) <= 2021:
                        # On récupère la colonne id de la ligne correspondant à l'utilisateur en session
                        Sitter = User.objects.filter(Email=request.session["User"])
                        # On formatte une date
                        Date = escape(int(request.GET["Day"])) + "/" +escape(int(request.GET["Month"])) + "/" + escape(int(request.GET["Year"]))
                        
                        if request.GET["City"] != "":
                            City = escape(request.GET["City"])
                        else:
                            City = None
                            
                        if request.GET["ChildMax"] != "":
                            ChildMax = escape(request.GET["ChildMax"])
                        else:
                            ChildMax = None
                        
                        # On créée une disponibilité
                        NewDisponibility = Disponibilities(
                            SitterId = Sitter[0].pk,
                            Date = Date,
                            Price = Sitter[0].Price,
                            City=City,
                            ChildMax=ChildMax
                        )
                        
                        NewDisponibility.save()
                        return redirect('/')
                    else:
                        return render(request, "AddDisponibility.html", {"Error": "Merci de choisir une année entre 2019 et 2021.", "SessionUser": SessionUser[0]} )
                else:
                    return render(request, "AddDisponibility.html", {"Error": "Merci de choisir un mois entre 1 et 12.", "SessionUser": SessionUser[0]})
            else:
                return render(request, "AddDisponibility.html", {"Error": "Merci de choisir un jour entre le 1 et le 31.", "SessionUser": SessionUser[0]})
        else:
            return render(request, "AddDisponibility.html", {"SessionUser": SessionUser[0]})
    else:
        return redirect('/')
    
def DeleteDisponibility(request):
    # On vérifie qu'un utilisateur est connecté
    if "User" in request.session:
        if len(request.GET) > 0:
            # Id de la disponibilité (pk)
            Id = int(escape(request.GET["Id"]))
            # On récupère les infos sur l'utilisateur connecté
            Query = User.objects.filter(Email=request.session["User"])
            # On récupère les infos sur la disponibilité visée
            Disponibility = Disponibilities.objects.filter(pk=Id)
            # On vérifie que la disponibilité et l'utilisateur existe
            if len(Query) > 0 and len(Disponibility) > 0:
                if Disponibility[0].SitterId == Query[0].pk:
                    Disponibilities.objects.filter(pk=Id).delete()
                    return redirect('/')
                else:
                    return redirect('/')
            else:
                return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('/')
    
def Search(request):
    if "User" in request.session:
        SessionUser = User.objects.filter(Email=request.session["User"])
        if len(request.GET) > 0:
            if request.GET["Day"] != "" and request.GET["Month"] != "" and request.GET["Year"] != "":
                if 0 < int(request.GET["Day"]) <= 31:
                    if 0 < int(request.GET["Month"]) <= 12:
                        if 2019 <= int(request.GET["Year"]) <= 2021:
                            # On formatte une date
                            Date = escape(int(request.GET["Day"])) + "/" +escape(int(request.GET["Month"])) + "/" + escape(int(request.GET["Year"]))
                            # On sélectionne toutes les disponibilités dont la date est égale à la date que l'on vient de formatter
                            Query = Disponibilities.objects.filter(Date=Date,Reserved=False).exclude(SitterId=User.objects.filter(Email=request.session["User"]))
                            
                            
                            if request.GET["ChildMax"] != "":
                                Query = Query.filter(ChildMax__gte=int(escape(request.GET["ChildMax"])))
                            
                            if request.GET["City"] != "":
                                Query = Query.filter(City=escape(request.GET["City"]))
                                
                            if request.GET["Max"] != "":
                                Query = Query.filter(Price__lte=int(escape(request.GET["Max"])))
                            
                            if len(Query) == 0:
                                return render(request, "Search.html", {"SessionUser": SessionUser[0], "Error": "Désolé, nous n'avons trouvé aucun baby-sitter de disponible à la date et aux tarifs demandés."})
                            else:
                                # Pour chaque Disponibilité, on ajoute un attribut à l'objet dispo (setattr()) égal à la valeur de cet attribut dans les infos du sitter
                                for Dispo in Query:
                                    setattr(Dispo, 'Price', User.objects.filter(pk=Dispo.SitterId)[0].Price)
                                    setattr(Dispo, 'Name', User.objects.filter(pk=Dispo.SitterId)[0].Firstname + " " + User.objects.filter(pk=Dispo.SitterId)[0].Lastname)
                                    setattr(Dispo, 'City', User.objects.filter(pk=Dispo.SitterId)[0].City)
                                    setattr(Dispo, 'Age', User.objects.filter(pk=Dispo.SitterId)[0].Age)
                                    setattr(Dispo, 'Infos', User.objects.filter(pk=Dispo.SitterId)[0].Infos)
                                    setattr(Dispo, 'Note', Note(User.objects.filter(pk=Dispo.SitterId)[0].pk))
                                    
                                return render(request, "Search.html", {"SessionUser": SessionUser[0], "Results": Query})
                        else:
                            return render(request, "Search.html", {"SessionUser": SessionUser[0], "Error": "Merci de choisir une année entre 2019 et 2021."} )
                    else:
                        return render(request, "Search.html", {"SessionUser": SessionUser[0],"Error": "Merci de choisir un mois entre 1 et 12."})
                else:
                    return render(request, "Search.html", {"SessionUser": SessionUser[0],"Error": "Merci de choisir un jour entre le 1 et le 31."})
            else:
                return render(request, "Search.html", {"SessionUser": SessionUser[0], "Error": "Merci de compléter tous les champs."})
        else:
            return render(request, "Search.html", {"SessionUser": SessionUser[0]})
    else:
        return redirect('/')
    
def Reserve(request):
    if "User" in request.session:
        SessionUser = User.objects.filter(Email=request.session["User"])
        if len(request.GET) > 0:
            if int(request.GET["End"]) - int(request.GET["Start"]) > 0:
                if 0 <= int(request.GET["End"]) <= 24 and 0 <= int(request.GET["Start"]) <= 24:
                    # On vérifie que l'utilisateur connecté ne puisse pas réserver sa propre disponibilité
                    if Disponibilities.objects.filter(pk=int(escape(request.GET["Id"])))[0].SitterId != User.objects.filter(Email=request.session["User"])[0].pk:
                        Duration = int(request.GET["End"]) - int(request.GET["Start"])
                        # On met à jour la ligne correspondant à la disponibilité
                        Disponibilities.objects.filter(pk=int(escape(request.GET["Id"]))).update(Reserved=True,By=User.objects.filter(Email=request.session["User"])[0].pk,Duration=Duration,Start=float(escape(request.GET["Start"])),End=float(escape(request.GET["End"])))
                        # On envoie un message à au babysitter
                        NewMessage = Message(
                            Target=Disponibilities.objects.filter(pk=int(escape(request.GET["Id"])))[0].SitterId,
                            Content="Bonne nouvelle ! Vous avez une nouvelle réservation pour l'une de vos dates !",
                            Link=int(escape(request.GET["Id"])),
                            Type="Success",
                        )
                        NewMessage.save()
                        return redirect('/Profile?Id='+str(SessionUser[0].pk))
                    else:
                        return redirect('/Search')
                else:
                    return render(request, 'Search.html', {"Error": "Merci d'entrer des heures de réservation raisonnables."})
            else:
                return render(request, 'Search.html', {"Error": "Merci d'entrer des heures de réservation raisonnables."})
        else:
            return redirect('/Search')
    else:
        return redirect("/Login")
    
def Users(request):
    if "User" in request.session:
        # On récupère les informations sur l'utilisateur connecté
        SessionUser = User.objects.filter(Email=request.session["User"])
        if len(request.GET) > 0:
            # On récupère les utilisateurs dont le prénom ou le nom contient la recherche
            Query = User.objects.filter(Firstname__contains=escape(request.GET["User"])).exclude(pk=SessionUser[0].pk)|User.objects.filter(Lastname__contains=escape(request.GET["User"])).exclude(pk=SessionUser[0].pk)
            Query.exclude(Banned=True)
            if len(Query) > 0:
                return render(request, "Users.html", {"Note": Note(Query[0].pk),"SessionUser": SessionUser[0], "Results": Query}) 
            else:
                return render(request, "Users.html", {"SessionUser": SessionUser[0], "Error": "Aucun profil n'a été trouvé."})
        else:
            return render(request, "Users.html", {"SessionUser": SessionUser[0]})
    else:
        return redirect('/Login')
    
def Profile(request):
    if "User" in request.session:
        if len(request.GET) > 0:
            # On récupère les informations sur l'utilisateur correspondant au paramètre Id
            Query = User.objects.filter(pk=int(escape(request.GET["Id"])))
            if len(Query) > 0:
                # On récupère les informations sur la session
                SessionUser = User.objects.filter(Email=request.session["User"])
                # Si on veut afficher son propre profil (autorisations supplémentaires)
                if SessionUser[0].pk == int(escape(request.GET["Id"])):
                    # On récupère toutes nos réservations
                    Reservations = Disponibilities.objects.filter(By=SessionUser[0].pk)
                    # On récupère tous nos babysitting à venir
                    UpComing = Disponibilities.objects.filter(SitterId=SessionUser[0].pk,Reserved=True)
                    
                    # On ajoute aux objets disponibilities des colonnes contenant des informations sur l'utilisateur ayant réservé
                    for Coming in UpComing:
                        setattr(Coming, 'Price', User.objects.filter(pk=Coming.By)[0].Price)
                        setattr(Coming, 'Name', User.objects.filter(pk=Coming.By)[0].Firstname + " " + User.objects.filter(pk=Coming.SitterId)[0].Lastname)
                        setattr(Coming, 'City', User.objects.filter(pk=Coming.By)[0].City)
                        setattr(Coming, 'Age', User.objects.filter(pk=Coming.By)[0].Age)
                        setattr(Coming, 'Infos', User.objects.filter(pk=Coming.By)[0].Infos)
                        
                    # On ajoute aux objets disponibilities des colonnes contenant des informations sur l'utilisateur proposant la disponibilité
                    for Reservation in Reservations:
                        setattr(Reservation, 'Price', User.objects.filter(pk=Reservation.SitterId)[0].Price)
                        setattr(Reservation, 'Name', User.objects.filter(pk=Reservation.SitterId)[0].Firstname + " " + User.objects.filter(pk=Reservation.SitterId)[0].Lastname)
                        setattr(Reservation, 'City', User.objects.filter(pk=Reservation.SitterId)[0].City)
                        setattr(Reservation, 'Age', User.objects.filter(pk=Reservation.SitterId)[0].Age)
                        setattr(Reservation, 'Infos', User.objects.filter(pk=Reservation.SitterId)[0].Infos)
                    
                    # On récupère vérifie si le profil visité fait partie de nos favoris
                    CheckForFavorite = Favorite.objects.filter(User=SessionUser[0].pk,FavoriteUser=int(escape(request.GET["Id"])))
                    if len(CheckForFavorite) > 0:
                        IsFavorite = True
                    else:
                        IsFavorite = False
                    
                    # Si l'utilisateur recherché est un babysitter
                    if Query[0].Status != "Parent":
                        # On calcule sa note moyenne
                        UserNote = Note(Query[0].pk)
                        # Si il est "both"
                        if Query[0].Status == "Both":
                            # On récupère la liste de ses enfants
                            Childs = Child.objects.filter(Parent=Query[0].pk)
                            return render(request, "Profile.html", {"User": Query[0], "SessionUser": SessionUser[0], "Reservations": Reservations, "UpComing": UpComing, "Note": UserNote, "Childs": Childs, "IsFavorite": IsFavorite})
                        else:
                            return render(request, "Profile.html", {"User": Query[0], "SessionUser": SessionUser[0], "Reservations": Reservations, "UpComing": UpComing, "Note": UserNote, "IsFavorite": IsFavorite})
                    else:
                        Childs = Child.objects.filter(Parent=Query[0].pk)
                        return render(request, "Profile.html", {"User": Query[0], "SessionUser": SessionUser[0], "Reservations": Reservations, "UpComing": UpComing, "Childs": Childs, "IsFavorite": IsFavorite})
                # Si on affiche le profil de quelqu'un d'autre
                else:
                    # On vérifie si l'utilisateur fait partie de nos favoris
                    CheckForFavorite = Favorite.objects.filter(User=SessionUser[0].pk,FavoriteUser=int(escape(request.GET["Id"])))
                    if len(CheckForFavorite) > 0:
                        IsFavorite = True
                    else:
                        IsFavorite = False
                        
                    # Si l'utilisateur recherché n'est pas un parent
                    if Query[0].Status != "Parent":
                        # On calcule sa not moyenne
                        UserNote = Note(Query[0].pk)
                        if Query[0].Status == "Both":
                            Childs = Child.objects.filter(Parent=Query[0].pk)
                            return render(request, "Profile.html", {"User": Query[0], "SessionUser": SessionUser[0], "Note": UserNote, "Childs": Childs, "IsFavorite": IsFavorite})
                        else:
                            return render(request, "Profile.html", {"User": Query[0], "SessionUser": SessionUser[0], "Note": UserNote, "IsFavorite": IsFavorite})
                    else:
                        Childs = Child.objects.filter(Parent=Query[0].pk)
                        return render(request, "Profile.html", {"User": Query[0], "SessionUser": SessionUser[0], "Childs": Childs, "IsFavorite": IsFavorite})
            else:
                return redirect('/Users', {"Error": "Cet utilisateur n'existe pas."})
        else:
            return redirect('/')
    else:
        return redirect('/Login')
    
def DeleteMessage(request):
    if len(request.GET)> 0:
        # On supprime la ligne correspondant au message dont la pk est Id
        Message.objects.filter(pk=int(escape(request.GET["Id"]))).delete()
        return redirect('/')
    else:
        return redirect('/')
    
def Cancel(request):
    if "User" in request.session:
        if len(request.GET) > 0:
            # On récupère la réservation à annuler
            Reservation = Disponibilities.objects.filter(pk=int(escape(request.GET["Id"])))
            # On récupère les informations sur la session
            SessionUser = User.objects.filter(Email=request.session["User"])
            # Si l'utilisateur connecté est l'auteur de la disponibilité
            if SessionUser[0].pk == Reservation[0].SitterId:
                # On crée le message
                NewMessage = Message(
                        Target=Reservation[0].By,
                        Content="Mauvaise nouvelle... L'une de vos réservation vient d'annuler le baby-sitting pour le " + Reservation[0].Date +".",
                        Link=int(escape(request.GET["Id"])),
                        Type="Error",
                )
                NewMessage.save()
                # On supprime la disponibilité
                Reservation[0].delete()
                return redirect('/Profile')
            else:
                return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('/Login')
    
def CancelReservation(request):
    if "User" in request.session:
        if len(request.GET) > 0:
            # On récupère la réservation à annuler
            Reservation = Disponibilities.objects.filter(pk=int(escape(request.GET["Id"])))
            # On récupère les informations sur la session
            SessionUser = User.objects.filter(Email=request.session["User"])
            # Si l'utilisateur connecté est l'auteur de la disponibilité
            if SessionUser[0].pk == Reservation[0].By:
                # On crée le message
                NewMessage = Message(
                        Target=Reservation[0].SitterId,
                        Content="Mauvaise nouvelle... L'une de vos réservation vient d'annuler sa réservation pour le " + Reservation[0].Date +".",
                        Link=int(escape(request.GET["Id"])),
                        Type="Error",
                )
                NewMessage.save()
                # On supprime la disponibilité
                Reservation[0].delete()
                return redirect('/Profile')
            else:
                return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('/Login')
    
def Details(request):
    if "User" in request.session:
        if len(request.GET) > 0:
            # On récupère les informations sur la session
            SessionUser = User.objects.filter(Email=request.session["User"])
            # On récupère toutes les informations sur la réservation dont on veut afficher les détails (pk=Id)
            Reservation = Disponibilities.objects.filter(pk=int(escape(request.GET["Id"])))
            # Si on est l'auteur de la disponibilité ou la personne qui l'a réservée: on peut voir les informations
            if SessionUser[0].pk == Reservation[0].SitterId or SessionUser[0].pk == Reservation[0].By:
                # On récupère toutes les informations sur le babysitter
                Sitter = User.objects.filter(pk=Reservation[0].SitterId)
                # On récupère toutes les informations sur le parent
                Parent = User.objects.filter(pk=Reservation[0].By)
                # On récupère le commentaire éventuel sur la réservation
                Comments = Comment.objects.filter(Reservation=Reservation[0].pk,Answer=False)
                # On récupère la réponse éventuelle au commentaire du parent
                Answers = Comment.objects.filter(Reservation=Reservation[0].pk,Answer=True)
                # Si on est le parent
                if SessionUser[0].pk == Reservation[0].By:
                    IsParent = True
                else:
                    IsParent = False
                # Si le parent a déjà commenté 
                if len(Comments) > 0:
                    IsCommented = True
                else:
                    IsCommented = False
                # Si le babysitter a déjà répondu au commentaire
                if len(Answers) > 0:
                    IsAnswered = True
                else:
                    IsAnswered = False
                if IsCommented:
                    if IsAnswered:
                        return render(request, "Details.html", {"SessionUser": SessionUser[0], "Reservation": Reservation[0], "Sitter": Sitter[0], "Parent": Parent[0], "IsParent": IsParent, "IsCommented": IsCommented, "Comment": Comments[0], "IsAnswered": True, "Answer": Answers[0]})
                    else:
                        return render(request, "Details.html", {"SessionUser": SessionUser[0], "Reservation": Reservation[0], "Sitter": Sitter[0], "Parent": Parent[0], "IsParent": IsParent, "IsCommented": IsCommented, "Comment": Comments[0]})
                else:
                    return render(request, "Details.html", {"SessionUser": SessionUser[0], "Reservation": Reservation[0], "Sitter": Sitter[0], "Parent": Parent[0], "IsParent": IsParent, "IsCommented": IsCommented})
            else:
                return redirect('/')
        else:
            return redirect('/Profile')
    else:
        return redirect('/Login')
    
def AddComment(request):
    if "User" in request.session:
        if len(request.GET) > 0:
            if request.GET["Comment"] != "":
                # On crée un commentaire
                NewComment= Comment(
                    Sitter=int(escape(request.GET["Sitter"])),
                    Parent=int(escape(request.GET["Parent"])),
                    Reservation=int(escape(request.GET["Reservation"])),
                    Note=int(escape(request.GET["Note"])),
                    Comment=escape(request.GET["Comment"])
                )
                NewComment.save()
                return redirect('/Details?Id='+escape(request.GET["Reservation"]))
            else:
                return redirect('/Details?Id='+escape(request.GET["Reservation"]))
        else:
            return redirect('/')
    else:
        return redirect('/Login')
    
def AddAnswer(request):
    if "User" in request.session:
        if len(request.GET) > 0:
            if request.GET["Answer"] != "":
                # On récupère les informations sur le commentaire auquel on répond
                Related = Comment.objects.filter(pk=int(escape(request.GET["Related"])))
                # Pour la redirection
                Target = int(Related[0].Reservation)
                # On créée la réponse
                NewAnswer = Comment(
                    Sitter=Related[0].Sitter,
                    Parent=Related[0].Parent,
                    Reservation=Related[0].Reservation,
                    Note=Related[0].Note,
                    Comment=escape(request.GET["Answer"]),
                    Answer=True,
                    Related=Related[0].pk
                )
                
                NewAnswer.save()
                return redirect("/Details?Id="+str(Target))
            else:
                return redirect("/Details?Id="+str(Target))
        else:
            return redirect('/Details?Id='+request.GET["Related"]) 
    else:
        return redirect('/Login')
    
def AddFavorite(request):
    if "User" in request.session:
        if len(request.GET) > 0:
            # On récupère toutes les informations sur la session
            SessionUser = User.objects.filter(Email=request.session["User"])
            # On  vérifie que l'utilisateur n'est pas déjà dans nos favoris
            Query = Favorite.objects.filter(User=SessionUser[0].pk,FavoriteUser=int(escape(request.GET["User"])))
            # Si l'utilisateur est déjà dans les favoris, on le retire
            if len(Query) > 0:
                Query.delete()
                return redirect('/Profile?Id='+request.GET["User"])
            # Si l'utilisateur n'est pas dans nos favoris, on l'ajoute
            else:
                NewFavorite = Favorite(
                    User=SessionUser[0].pk,
                    FavoriteUser=int(escape(request.GET["User"]))
                )
                
                NewFavorite.save()
                return redirect('/Profile?Id='+request.GET["User"])
        else:
            return redirect('/')
    else:
        return redirect('/Login')

def Chatter(request):
    if "User" in request.session:
        if len(request.GET) > 0:
            Sender = User.objects.filter(Email=request.session["User"])
            Receiver = User.objects.filter(pk=escape(request.GET["User"]))
            Chats = Chat.objects.filter(Sender=Sender[0].pk,Receiver=int(escape(request.GET["User"])))|Chat.objects.filter(Sender=int(escape(request.GET["User"])),Receiver=Sender[0].pk)
            if len(Sender) > 0 and len(Receiver) > 0:
                return render(request, 'Chat.html', {"Sender": Sender[0], "Receiver": Receiver[0], "Chats": Chats})
            else:
                return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('/Login')
    
def Send(request):
    if "User" in request.session:
        if len(request.GET) > 0:
            if request.GET["Content"] != "":
                NewChat = Chat(
                    Sender=int(escape(request.GET["Sender"])),
                    Receiver=int(escape(request.GET["Receiver"])),
                    Content=escape(request.GET["Content"]),
                )
                
                NewChat.save()
                return redirect('/Chat?User='+request.GET["Receiver"])
            else:
                return redirect('/Chat?User='+request.GET["Receiver"])
        else:
            return redirect('/Chat?User='+request.GET["Receiver"])
    else:
        return redirect('/Login')

def AddReport(request):
    if "User" in request.session:
        if len(request.GET) > 0:
            SessionUser = User.objects.filter(Email=request.session["User"])
            Query = User.objects.filter(pk=int(escape(request.GET["User"]))).exclude(Banned=True)
            if len(Query) > 0:
                if "Comment" in request.GET:
                    if request.GET["Comment"] != "":
                        NewReport = Report(
                            Reported = Query[0].pk,
                            By=SessionUser[0].pk,
                            Comment = escape(request.GET["Comment"])
                        )
                        
                        NewReport.save()
                        return render(request, 'Report.html', {"User": Query[0], "SessionUser": SessionUser[0], "Success": "L'utilisateur a été signalé avec succès !"})
                    else:
                        return render(request, 'Report.html', {"User": Query[0], "SessionUser": SessionUser[0], "Error": "Le commentaire est obligatoire."})
                else:
                    return render(request, 'Report.html', {"User": Query[0], "SessionUser": SessionUser[0]})
            else:
                return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('/Login')
    
def Reports(request):
    if "User" in request.session:
        SessionUser = User.objects.filter(Email=request.session["User"])
        if SessionUser[0].Admin:
            if len(request.GET) > 0:
                return redirect('/')
            else:
                Items = Report.objects.all().order_by("-Date")
                for Item in Items:
                    setattr(Item, "Name", User.objects.filter(pk=Item.Reported)[0].Firstname + " " + User.objects.filter(pk=Item.Reported)[0].Lastname)
                    setattr(Item, "ByUser", User.objects.filter(pk=Item.By)[0].Firstname + " " + User.objects.filter(pk=Item.By)[0].Lastname)
                    
                return render(request, "Reports.html", {"Items": Items})
        else:
            return redirect('/')
    else:
        return redirect('/Login')
    
def Ban(request):
    if "User" in request.session:
        SessionUser = User.objects.filter(Email=request.session["User"])
        if SessionUser[0].Admin:
            if len(request.GET) > 0:
                if "User" in request.GET:
                    User.objects.filter(pk=int(escape(request.GET["User"]))).update(Banned=True)
                    Report.objects.filter(Reported=int(escape(request.GET["User"]))).delete()
                    return redirect('/Reports')
                else:
                    return redirect('/')
            else:
                return redirect('/')
        else:
            return redirect('/')
    else:
        return redirect('/Login')

#Fonctions
def Note(Id):
    # On récupère toutes les notes sur nos babysitting
    Comments = Comment.objects.filter(Sitter=int(escape(Id)))
    if len(Comments) > 0:
        Sum = 0
        for Item in Comments:
            Sum += Item.Note
            # On fait la moyenne des notes
        return Sum/len(Comments)
    else:
        return "Aucune note"
    
def Profit(Id):
    # On récupère tous nos babysitting
    Sitting = Disponibilities.objects.filter(SitterId=Id, Reserved=True)
    # On récupère nos réservations
    Reservations = Disponibilities.objects.filter(By=Id)
    # On met nos dépenses et recettes à 0
    Income = 0
    Outcome = 0
    if len(Sitting) > 0:
        for Sit in Sitting:
            Income += Sit.Price*Sit.Duration
        
    if len(Reservations) > 0:
        for Res in Reservations:
            Outcome += Res.Price*Res.Duration
    # On fait la différence entre les entrées et les dépenses 
    return Income - Outcome
    
    
    
    
    
    
    