import random
from django.core.management.base import BaseCommand, CommandParser

from faker import Faker
from django_seed import Seed
# from users.models import User
from posts.models import Post
from images.models import Image
from petCategories.models import Pet
from boardCategories.models import Category
from django.contrib.auth import get_user_model
User = get_user_model()


class Command(BaseCommand):
    help="generate random data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            default=0,
            type=int,
            help="how many post? you make"
        )

    def handle(self, *args, **options):
        fake=Faker('ko_KR')
        count=options["count"]

        # make post
        # fake=Faker('ko_KR')가 text, word에는 한국어 미적용된다고 함..
        #  그렇다면 검색엔진을 한국어로 설정할 필요가 있나?(<- 보류:한국어 설정 )
        users = User.objects.all()
        print("users: ", users)
        # for user in users:
        for _ in range(count):
            post=Post.objects.create(
                user=User.objects.order_by("?").first(),
                content=fake.text(max_nb_chars=550),
                categoryType= Category.objects.order_by("?").first()
            )

            pet_objects = random.sample(list(Pet.objects.all()), random.randint(1, 3))
            print("pet_objects: ", pet_objects)
            post.boardAnimalTypes.set(pet_objects) 
            print("add success")

        
        self.stdout.write(self.style.SUCCESS(f"총 {count}개의 게시글을 성공적으로 생성했습니다."))
