from company.models import Author, Company 
from jobs.models import HNLink, Post 

def create_author(data: dict):
    name, link = data['name'], data['link']
    author, is_created = Author.objects.get_or_create(name=name, link=link)
    return author


def create_company(name: str):
    company, is_created = Company.objects.get_or_create(name=name)
    return company


def create_hnlink(month: str, year: str, link: str, count: int):
    obj, is_created = HNLink.objects.get_or_create(month=month, year=year, link=link)
    obj.count = count
    obj.save()


def create_post(month, year, company_name, data: dict):
    author = create_author(data['author'])
    company = create_company(company_name)

    post, _ = Post.objects.get_or_create(
        month=month,
        year=year,
        author=author,
        company=company,
        role=data.get("role"),
        body=data.get("body"),
        link=data.get("post_link"),
        links=data.get("links", []),
    )

