import random
from django.core.management.base import BaseCommand, CommandParser

from faker import Faker
from django_seed import Seed
from users.models import User
from posts.models import Post
from petCategories.models import Pet
from boardCategories.models import Board
from addresses.models import Address
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
        board_choices = list(Board.objects.all())
        pet_choices = list(Pet.objects.all())
        
        for user in users:
            user_address = Address.objects.filter(user=user).first()
            for _ in range(count):
                board = random.choice(board_choices)
                num_pets = random.randint(1, len(pet_choices))
                pets = random.sample(pet_choices, k=num_pets) if num_pets > 0 else []

                post = Post(
                    author=user,
                    content=fake.text(),
                    categoryType=board,
                    viewCount=random.randint(0, 100),
                    postImage=fake.image_url(),
                    address=user_address
                )
                post.save()
                post.boardAnimalTypes.set(pets)
        
        self.stdout.write(self.style.SUCCESS(f"총 {count}개의 게시글을 성공적으로 생성했습니다."))
