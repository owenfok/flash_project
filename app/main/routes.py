from datetime import datetime
from flask import render_template, flash, redirect, url_for, request, g
from flask_login import current_user, login_required
from flask_babel import _, get_locale
from app import current_app, db
from app.main.forms import EditProfileForm, PostForm, InfoEditionsForm, InfoEditionsDESCForm, CloudServiceForm, \
    MainProductForm, ServiceForm, ServiceTypeForm, PartnersContentForm, WhySQLForm, WhySQLContentForm, \
    HowToBuyForm, ContactForm, EventsForm,CountryForm
from app.models import User, Post, infoEditions, infoEditionsdesc, cloudService, mainProduct, \
    Service, serviceType, partnersContent, whysql, whysqlContent, Contact, Events,howtobuy,Region,Country
from app.main import bp
from functools import wraps
from werkzeug.utils import secure_filename


@bp.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()
    g.locale = str(get_locale())


def is_admin(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        try:
            if current_user.username == 'admin':
                return func(*args, **kwargs)
            else:
                raise
        except:
            return render_template('errors/404.html'), 404

    return decorated_view


@bp.route('/', methods=['GET', 'POST'])
def home():
    ads = mainProduct.query.all()
    return render_template('home.html', ads=ads)


@bp.route('/partners', methods=['GET', 'POST'])
def partners():
    partner = partnersContent.query.all()
    return render_template('partner.html', title=_('Partner'), partner=partner)


@bp.route('/events', methods=['GET', 'POST'])
def events():
    event = Events.query.all()
    return render_template('events.html', title=_('Events'), event=event)


@bp.route('/buy-mysql', methods=['GET', 'POST'])
def howtobuy():
    contact = Contact.query.all()
    return render_template('howtobuy.html', title=_('How To Buy'),contact=contact)

@bp.route('/product', methods=['GET', 'POST'])
def product():
    edition = infoEditions.query.all()
    return render_template('product.html', title=_('Product'), edition=edition)

@bp.route('/about', methods=['GET', 'POST'])
def about():
    return render_template('about.html', title=_('About'))


@bp.route('/products/standard', methods=['GET', 'POST'])
def standard():
    link = infoEditions.query.all()
    intro = infoEditions.query.filter_by(id=1)
    edition = infoEditionsdesc.query.filter_by(infoeditions_id=1).all()
    return render_template('standard_products.html', title=_('Standard'), edition=edition, link=link, intro=intro)


@bp.route('/products/enterprise', methods=['GET', 'POST'])
def enterprise():
    link = infoEditions.query.all()
    intro = infoEditions.query.filter_by(id=2)
    edition = infoEditionsdesc.query.filter_by(infoeditions_id=2).all()
    return render_template('standard_products.html', title=_('Enterprise'), edition=edition, link=link, intro=intro)


@bp.route('/products/cluster', methods=['GET', 'POST'])
def cluster():
    link = infoEditions.query.all()
    intro = infoEditions.query.filter_by(id=3)
    edition = infoEditionsdesc.query.filter_by(infoeditions_id=3).all()
    return render_template('standard_products.html', title=_('Cluster'), edition=edition, link=link, intro=intro)


@bp.route('/cloud', methods=['GET', 'POST'])
def cloud():
    delivers1 = cloudService.query.filter_by(even=1)
    delivers2 = cloudService.query.filter_by(even=2)
    return render_template('cloud.html', title=_('Cloud'), delivers1=delivers1, delivers2=delivers2)


@bp.route('/services', methods=['GET', 'POST'])
def services():
    service = Service.query.all()
    return render_template('services.html', title=_('Services'), service=service)


@bp.route('/training', methods=['GET', 'POST'])
def training():
    link = Service.query.all()
    st = serviceType.query.filter_by(service_id=1)
    return render_template('training.html', title=_('Training'), link=link, st=st)


@bp.route('/certification', methods=['GET', 'POST'])
def certification():
    link = Service.query.all()
    st = serviceType.query.filter_by(service_id=2)
    return render_template('certification.html', title=_('Certification'), link=link, st=st)


@bp.route('/support', methods=['GET', 'POST'])
def support():
    link = Service.query.all()
    st = serviceType.query.filter_by(service_id=3).all()
    return render_template('support.html', title=_('Support'), link=link, st=st)


@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    contact = Contact.query.all()
    return render_template('contact.html', title=_('Contact'), contact=contact)


@bp.route('/why-mysql', methods=['GET', 'POST'])
def why_mysql():
    wm = whysql.query.all()
    return render_template('why-mysql.html', title=_('whysql'), wm=wm)


@bp.route('/why-mysql/white-papers', methods=['GET', 'POST'])
def why_mysql_content():
    wm = whysql.query.all()
    t = whysql.query.filter_by(id=1)
    ct = whysqlContent.query.filter_by(whysql_id=1).all()
    return render_template('standard_mysql_content.html', title=_('White Papers'), wm=wm, ct=ct, t=t)


@bp.route('/why-mysql/presentations', methods=['GET', 'POST'])
def presentations():
    wm = whysql.query.all()
    t = whysql.query.filter_by(id=2)
    ct = whysqlContent.query.filter_by(whysql_id=2).all()
    return render_template('standard_mysql_content.html', title=_('Presentations'), wm=wm, ct=ct, t=t)


@bp.route('/why-mysql/tb', methods=['GET', 'POST'])
def tb():
    wm = whysql.query.all()
    return render_template('why-mysql-tb.html', title=_('T and B'), wm=wm)


@bp.route('/forum', methods=['GET', 'POST'])
@login_required
def forum():
    form = PostForm()
    if form.validate_on_submit():
        post = Post(body=form.post.data, author=current_user)
        db.session.add(post)
        db.session.commit()
        flash(_('Your post is now live!'))
        return redirect(url_for('main.forum'))
    page = request.args.get('page', 1, type=int)
    posts = current_user.followed_posts().paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.forum', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.forum', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('forum.html', title=_('Forum'), form=form,
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/explore')
@login_required
def explore():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.explore', page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.explore', page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('forum.html', title=_('Explore'),
                           posts=posts.items, next_url=next_url,
                           prev_url=prev_url)


@bp.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    page = request.args.get('page', 1, type=int)
    posts = user.posts.order_by(Post.timestamp.desc()).paginate(
        page, current_app.config['POSTS_PER_PAGE'], False)
    next_url = url_for('main.user', username=user.username, page=posts.next_num) \
        if posts.has_next else None
    prev_url = url_for('main.user', username=user.username, page=posts.prev_num) \
        if posts.has_prev else None
    return render_template('user.html', user=user, posts=posts.items,
                           next_url=next_url, prev_url=prev_url)


@bp.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash(_('Your changes have been saved.'))
        return redirect(url_for('main.edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title=_('Edit Profile'),
                           form=form)


@bp.route('/follow/<username>')
@login_required
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.forum'))
    if user == current_user:
        flash(_('You cannot follow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    db.session.commit()
    flash(_('You are following %(username)s!', username=username))
    return redirect(url_for('main.user', username=username))


@bp.route('/unfollow/<username>')
@login_required
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(_('User %(username)s not found.', username=username))
        return redirect(url_for('main.forum'))
    if user == current_user:
        flash(_('You cannot unfollow yourself!'))
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    db.session.commit()
    flash(_('You are not following %(username)s.', username=username))
    return redirect(url_for('main.user', username=username))


# admin_func
@bp.route('/database_index', methods=['GET', 'POST'])
@is_admin
def database_index():
    return render_template('edit_database/DatabaseIndex.html')


@bp.route('/info_editions', methods=['GET', 'POST'])
@is_admin
def edition_form():
    form = InfoEditionsForm()
    editions = infoEditions.query.all()
    if form.validate_on_submit():
        edition = infoEditions(title=form.title.data, content=form.content.data, url=form.url.data)
        db.session.add(edition)
        db.session.commit()
        flash(_('Added'))
        return redirect(url_for('main.edition_form'))
    if request.method == 'POST':
        del_form = request.form
        for ID in del_form.to_dict():
            record_id = ID
        del_edition = infoEditions.query.filter_by(id=record_id).first()
        db.session.delete(del_edition)
        db.session.commit()
        flash(_('Deleted'))
        return redirect(url_for('main.edition_form'))
    return render_template('edit_database/InfoEditionsForm.html', form=form, editions=editions)


@bp.route('/info_editions/<data_id>', methods=['GET', 'POST'])
@is_admin
def edition_form_id(data_id):
    form = InfoEditionsForm()
    edition = infoEditions.query.filter_by(id=data_id).first()
    if form.validate_on_submit():
        edition.title = form.title.data
        edition.content = form.content.data
        edition.url = form.url.data
        db.session.commit()
        flash(_('Updated'))
        return redirect(url_for('main.edition_form'))
    return render_template('edit_database/InfoEditionsForm.html', form=form, edition=edition, update=True)


@bp.route('/info_editions_description', methods=['GET', 'POST'])
@is_admin
def edition_desc_form():
    form = InfoEditionsDESCForm()
    descriptions = infoEditionsdesc.query.all()
    if form.validate_on_submit():
        description = infoEditionsdesc(title=form.title.data, content=form.content.data,
                                       infoeditions_id=form.infoeditions_id.data)
        db.session.add(description)
        db.session.commit()
        flash(_('Added'))
        return redirect(url_for('main.edition_desc_form'))
    if request.method == 'POST':
        del_form = request.form
        for ID in del_form.to_dict():
            record_id = ID
        del_edition_desc = infoEditionsdesc.query.filter_by(id=record_id).first()
        db.session.delete(del_edition_desc)
        db.session.commit()
        flash(_('Deleted'))
        return redirect(url_for('main.edition_desc_form'))
    return render_template('edit_database/InfoEditionsDescription.html', form=form, descriptions=descriptions)


@bp.route('/info_editions_description/<data_id>', methods=['GET', 'POST'])
@is_admin
def edition_desc_form_id(data_id):
    form = InfoEditionsDESCForm()
    description = infoEditions.query.filter_by(id=data_id).first()
    if form.validate_on_submit():
        description.title = form.title.data
        description.content = form.content.data
        description.infoeditions_id = form.infoeditions_id.data
        db.session.commit()
        flash(_('Updated'))
        return redirect(url_for('main.edition_desc_form'))
    return render_template('edit_database/InfoEditionsDescription.html', form=form, description=description,
                           update=True)


@bp.route('/info_cloudservice', methods=['GET', 'POST'])
@is_admin
def cloudservice_form():
    form = CloudServiceForm()
    services = cloudService.query.all()
    if form.validate_on_submit():
        service = cloudService(title=form.title.data, content=form.content.data, even=form.even.data)
        db.session.add(service)
        db.session.commit()
        flash(_('Added'))
        return redirect(url_for('main.cloudservice_form'))
    if request.method == 'POST':
        del_form = request.form
        for ID in del_form.to_dict():
            record_id = ID
        del_service = cloudService.query.filter_by(id=record_id).first()
        db.session.delete(del_service)
        db.session.commit()
        flash(_('Deleted'))
        return redirect(url_for('main.cloudservice_form'))
    return render_template('edit_database/InfoCloudService.html', form=form, services=services)


@bp.route('/info_cloudservice/<data_id>', methods=['GET', 'POST'])
@is_admin
def cloudservice_form_id(data_id):
    form = CloudServiceForm()
    service = cloudService.query.filter_by(id=data_id).first()
    if form.validate_on_submit():
        service.title = form.title.data
        service.content = form.content.data
        service.even = form.even.data
        db.session.commit()
        flash(_('Updated'))
        return redirect(url_for('main.cloudservice_form'))
    return render_template('edit_database/InfoCloudService.html', form=form, service=service, update=True)


@bp.route('/main_product', methods=['GET', 'POST'])
@is_admin
def info_main_productForm():
    form = MainProductForm()
    mainproducts = mainProduct.query.all()
    if form.validate_on_submit():
        mainproduct = mainProduct(title=form.title.data, intro=form.intro.data,
                                  url=form.url.data, icon=form.icon.data)
        db.session.add(mainproduct)
        db.session.commit()
        flash(_('Added'))
        return redirect(url_for('main.info_main_productForm'))
    if request.method == 'POST':
        del_form = request.form
        for ID in del_form.to_dict():
            record_id = ID
        del_mainproduct = mainProduct.query.filter_by(id=record_id).first()
        db.session.delete(del_mainproduct)
        db.session.commit()
        flash(_('Deleted'))
        return redirect(url_for('main.info_main_productForm'))
    return render_template('edit_database/InfoMainProductForm.html', form=form, mainproducts=mainproducts)


@bp.route('/main_product/<data_id>', methods=['GET', 'POST'])
@is_admin
def info_main_productForm_id(data_id):
    form = MainProductForm()
    mainproduct = mainProduct.query.filter_by(id=data_id).first()
    if form.validate_on_submit():
        mainproduct.title = form.title.data
        mainproduct.intro = form.intro.data
        mainproduct.url = form.url.data
        mainproduct.icon = form.icon.data
        db.session.commit()
        flash(_('Updated'))
        return redirect(url_for('main.info_main_productForm'))
    return render_template('edit_database/InfoMainProductForm.html', form=form, mainproduct=mainproduct, update=True)


@bp.route('/partners_content', methods=['GET', 'POST'])
@is_admin
def partners_content():
    form = PartnersContentForm()
    contents = partnersContent.query.all()
    if form.validate_on_submit():
        content = partnersContent(c_title=form.c_title.data, content=form.content.data)
        db.session.add(content)
        db.session.commit()
        flash(_('Added'))
        return redirect(url_for('main.partners_content'))
    if request.method == 'POST':
        del_form = request.form
        for ID in del_form.to_dict():
            record_id = ID
        del_content = partnersContent.query.filter_by(id=record_id).first()
        db.session.delete(del_content)
        db.session.commit()
        flash(_('Deleted'))
        return redirect(url_for('main.partners_content'))
    return render_template('edit_database/InfoPartnersContentForm.html', form=form, contents=contents)


@bp.route('/partners_content/<data_id>', methods=['GET', 'POST'])
@is_admin
def partners_content_id(data_id):
    form = PartnersContentForm()
    content = partnersContent.query.filter_by(id=data_id).first()
    if form.validate_on_submit():
        content.c_title = form.c_title.data
        content.content = form.content.data
        db.session.commit()
        flash(_('Updated'))
        return redirect(url_for('main.partners_content'))
    return render_template('edit_database/InfoPartnersContentForm.html', form=form, content=content, update=True)


@bp.route('/info_service', methods=['GET', 'POST'])
@is_admin
def edit_service():
    form = ServiceForm()
    servicess = Service.query.all()
    if form.validate_on_submit():
        service = Service(name=form.name.data, intro=form.intro.data, url=form.url.data)
        db.session.add(service)
        db.session.commit()
        flash(_('Added'))
        return redirect(url_for('main.edit_service'))
    if request.method == 'POST':
        del_form = request.form
        for ID in del_form.to_dict():
            record_id = ID
        del_service = Service.query.filter_by(id=record_id).first()
        db.session.delete(del_service)
        db.session.commit()
        flash(_('Deleted'))
        return redirect(url_for('main.edit_service'))
    return render_template('edit_database/InfoServiceForm.html', form=form, servicess=servicess)


@bp.route('/info_service/<data_id>', methods=['GET', 'POST'])
@is_admin
def edit_service_id(data_id):
    form = ServiceForm()
    services = Service.query.filter_by(id=data_id).first()
    if form.validate_on_submit():
        services.name = form.name.data
        services.intro = form.intro.data
        services.url = form.url.data
        db.session.commit()
        flash(_('Updated'))
        return redirect(url_for('main.edit_service'))
    return render_template('edit_database/InfoServiceForm.html', form=form, services=services, update=True)


@bp.route('/info_service_type', methods=['GET', 'POST'])
@is_admin
def edit_service_type():
    form = ServiceTypeForm()
    servicet = serviceType.query.all()
    if form.validate_on_submit():
        st = serviceType(title=form.title.data, content=form.content.data, service_id=form.service_id.data)
        db.session.add(st)
        db.session.commit()
        flash(_('Added'))
        return redirect(url_for('main.edit_service_type'))
    if request.method == 'POST':
        del_form = request.form
        for ID in del_form.to_dict():
            record_id = ID
        del_service = serviceType.query.filter_by(id=record_id).first()
        db.session.delete(del_service)
        db.session.commit()
        flash(_('Deleted'))
        return redirect(url_for('main.edit_service_type'))
    return render_template('edit_database/InfoServiceTypeForm.html', form=form, servicet=servicet)


@bp.route('/info_service_type/<data_id>', methods=['GET', 'POST'])
@is_admin
def edit_service_type_id(data_id):
    form = ServiceTypeForm()
    st = serviceType.query.filter_by(id=data_id).first()
    if form.validate_on_submit():
        st.title = form.title.data
        st.content = form.content.data
        st.service_id = form.service_id.data
        db.session.commit()
        flash(_('Updated'))
        return redirect(url_for('main.edit_service_type'))
    return render_template('edit_database/InfoServiceTypeForm.html', form=form, st=st, update=True)


@bp.route('/info_whysql', methods=['GET', 'POST'])
@is_admin
def edit_whysql():
    form = WhySQLForm()
    sqls = whysql.query.all()
    if form.validate_on_submit():
        sql = whysql(name=form.name.data, url=form.url.data)
        db.session.add(sql)
        db.session.commit()
        flash(_('Added'))
        return redirect(url_for('main.edit_whysql'))
    if request.method == 'POST':
        del_form = request.form
        for ID in del_form.to_dict():
            record_id = ID
        del_sql = whysql.query.filter_by(id=record_id).first()
        db.session.delete(del_sql)
        db.session.commit()
        flash(_('Deleted'))
        return redirect(url_for('main.edit_whysql'))
    return render_template('edit_database/InfoWhySQLForm.html', form=form, sqls=sqls)


@bp.route('/info_whysql/<data_id>', methods=['GET', 'POST'])
@is_admin
def edit_whysql_id(data_id):
    form = WhySQLForm()
    sql = whysql.query.filter_by(id=data_id).first()
    if form.validate_on_submit():
        sql.name = form.name.data
        sql.url = form.url.data
        db.session.commit()
        flash(_('Updated'))
        return redirect(url_for('main.edit_whysql'))
    return render_template('edit_database/InfoWhySQLForm.html', form=form, sql=sql, update=True)


@bp.route('/info_whysql_content', methods=['GET', 'POST'])
@is_admin
def edit_whysql_content():
    form = WhySQLContentForm()
    sql_contents = whysqlContent.query.all()
    if form.validate_on_submit():
        sql_content = whysqlContent(title=form.title.data, content=form.content.data, whysql_id=form.whysql_id.data)
        db.session.add(sql_content)
        db.session.commit()
        flash(_('Added'))
        return redirect(url_for('main.edit_whysql_content'))
    if request.method == 'POST':
        del_form = request.form
        for ID in del_form.to_dict():
            record_id = ID
        del_sql_content = whysqlContent.query.filter_by(id=record_id).first()
        db.session.delete(del_sql_content)
        db.session.commit()
        flash(_('Deleted'))
        return redirect(url_for('main.edit_whysql_content'))
    return render_template('edit_database/InfoWhySQLContentForm.html', form=form, sql_contents=sql_contents)


@bp.route('/info_whysql_content/<data_id>', methods=['GET', 'POST'])
@is_admin
def edit_whysql_content_id(data_id):
    form = WhySQLContentForm()
    sql_content = whysqlContent.query.filter_by(id=data_id).first()
    if form.validate_on_submit():
        sql_content.title = form.title.data
        sql_content.content = form.content.data
        sql_content.whysql_id = form.whysql_id.data
        db.session.commit()
        flash(_('Updated'))
        return redirect(url_for('main.edit_whysql_content'))
    return render_template('edit_database/InfoWhySQLContentForm.html', form=form, sql_content=sql_content, update=True)


@bp.route('/info_howtobuy', methods=['GET', 'POST'])
@is_admin
def edit_howtobuy():
    form = HowToBuyForm()
    htbs = howtobuy.query.all()
    if form.validate_on_submit():
        htb = htb(title=form.title.data, content=form.content.data, url=form.url.data)
        db.session.add(htb)
        db.session.commit()
        flash(_('Added'))
        return redirect(url_for('main.edit_howtobuy'))
    if request.method == 'POST':
        del_form = request.form
        for ID in del_form.to_dict():
            record_id = ID
        del_htb = howtobuy.query.filter_by(id=record_id).first()
        db.session.delete(del_htb)
        db.session.commit()
        flash(_('Deleted'))
        return redirect(url_for('main.edit_howtobuy'))
    return render_template('edit_database/InfoHTBForm.html', form=form, htbs=htbs)


@bp.route('/info_howtobuy/<data_id>', methods=['GET', 'POST'])
@is_admin
def edit_howtobuy_id(data_id):
    form = HowToBuyForm()
    htb = howtobuy.query.filter_by(id=data_id).first()
    if form.validate_on_submit():
        howtobuy.title = form.title.data
        howtobuy.content = form.content.data
        howtobuy.url = form.url.data
        db.session.commit()
        flash(_('Updated'))
        return redirect(url_for('main.edit_howtobuy'))
    return render_template('edit_database/InfoHTBForm.html', form=form, htb=htb, update=True)

@bp.route('/addcountry', methods=['GET', 'POST'])
def addcountry():
    form = CountryForm()
    if form.validate_on_submit():
        country=Country(country=form.country.data)
        db.session.add(country)
        db.session.commit()
        flash(_('Added'))
        return redirect(url_for('main.database_index'))
    return render_template('edit_database/addcountry.html', form=form)

@bp.route('/edit_contacts', methods=['GET', 'POST'])
# @is_admin
def edit_contacts():
    form = ContactForm()
    form.region.choices = [(s.id, s.region) for s in db.session.query(Region).all()]
    form.country.choices = [(s.id, s.country) for s in db.session.query(Country).all()]
    contacts = Contact.query.all()
    if form.validate_on_submit():
        filename = secure_filename(form.flag.data.filename)
        form.flag.data.save('/WEB_EA/app/static/img/' + filename)
        contact = Contact(region_id=form.region.data, country_id=form.country.data, phone=form.phone.data,
                          email=form.email.data, flag=filename)
        db.session.add(contact)
        db.session.commit()
        flash(_('Added'))
        return redirect(url_for('main.edit_contacts'))
    if request.method == 'POST':
        del_form = request.form
        for ID in del_form.to_dict():
            record_id = ID
        del_contact = Contact.query.filter_by(id=record_id).first()
        db.session.delete(del_contact)
        db.session.commit()
        flash(_('Deleted'))
        return redirect(url_for('main.edit_contacts'))
    return render_template('edit_database/EditContacts.html', form=form, contacts=contacts)


@bp.route('/edit_contacts/<data_id>', methods=['GET', 'POST'])
@is_admin
def edit_contacts_id(data_id):
    form = ContactForm()
    form.region.choices = [(s.id, s.region) for s in db.session.query(Region).all()]
    form.country.choices = [(s.id, s.country) for s in db.session.query(Country).all()]
    contact = Contact.query.filter_by(id=data_id).first()
    if form.validate_on_submit():
        filename = secure_filename(form.flag.data.filename)
        form.flag.data.save('/WEB_EA/app/static/img/' + filename)
        contact.region_id = form.region.data
        contact.country_id = form.country.data
        contact.phone = form.phone.data
        contact.email = form.email.data
        contact.flag = filename
        db.session.commit()
        flash(_('Updated'))
        return redirect(url_for('main.edit_contacts'))
    return render_template('edit_database/EditContacts.html', form=form, contact=contact, update=True)


@bp.route('/edit_events', methods=['GET', 'POST'])
@is_admin
def edit_events():
    form = EventsForm()
    events = Events.query.all()
    if form.validate_on_submit():
        event = Events(Events_title=form.Events_title.data, Events_time=form.Events_time.data,
                       Events_city=form.Events_city.data,
                       Events_country=form.Events_country.data, Events_intro=form.Events_intro.data)
        db.session.add(event)
        db.session.commit()
        flash(_('Added'))
        return redirect(url_for('main.edit_events'))
    if request.method == 'POST':
        del_form = request.form
        for ID in del_form.to_dict():
            record_id = ID
        del_event = Events.query.filter_by(id=record_id).first()
        db.session.delete(del_event)
        db.session.commit()
        flash(_('Deleted'))
        return redirect(url_for('main.edit_events'))
    return render_template("edit_database/EditEvents.html", form=form, events=events)


@bp.route('/edit_events/<data_id>', methods=['GET', 'POST'])
@is_admin
def edit_events_id(data_id):
    form = EventsForm()
    event = Events.query.filter_by(id=data_id).first()
    if form.validate_on_submit():
        event.Events_title = form.Events_title.data
        event.Events_time = form.Events_time.data
        event.Events_city = form.Events_city.data
        event.Events_country = form.Events_country.data
        event.Events_intro = form.Events_intro.data
        db.session.commit()
        flash(_('Updated'))
        return redirect(url_for('main.edit_events'))
    return render_template('edit_database/EditEvents.html', form=form, event=event, update=True)
