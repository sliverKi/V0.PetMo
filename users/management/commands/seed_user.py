import random
from django.core.management.base import BaseCommand, CommandParser

from faker import Faker
from django_seed import Seed
from users.models import User
from addresses.models import Address
from posts.models import Post

from petCategories.models import Pet
from boardCategories.models import Board

class Command(BaseCommand):
    help="generate random data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--count",
            default=0,
            type=int,
            help="how many user? you make"
        )
    

    def handle(self, *args, **options):
        fake=Faker(['ko_KR'])
        count=options["count"]

        # make user
        user_seeder = Seed.seeder()
        print("first seeder: ", user_seeder)
        user_seeder.add_entity(User, count, {
            "username": lambda x : fake.user_name(),
            "email": lambda x : fake.email(),
            "profile": lambda x: fake.url(),
            "hasPet": lambda x : random.choice([True, False]),
            "first": True,
            "is_staff": False,
            "is_active": True,
            "dated_joined": fake.date_time_this_decade(),
        })
        
        user_inserted_pks = user_seeder.execute()
        print("user inserted_pks: ", user_inserted_pks)

        user_ids = [pk for model, pks in user_inserted_pks.items() if model == User for pk in pks]
        print("user_ids: ", user_ids)

        # print("a: ",fake.address())

        for user_id in user_ids:
            user = User.objects.get(id=user_id)
            print("user: ", user)
            if user.hasPet:
                num_pets = random.randint(1,3)
                pets = random.sample(list(Pet.objects.all()), num_pets)
                user.pets.set(pets)

             # Faker로부터 랜덤 주소 생성
            fake_address = fake.address()
            regions = fake_address.split()
            address = Address.objects.create(
                user=user,
                addressName=fake_address,
                regionDepth1=regions[0],
                regionDepth2=regions[1],
                regionDepth3=regions[2] if len(regions) > 2 else '',
            )        

            user.address = address
            user.save()
        self.stdout.write(self.style.SUCCESS(f"총 {count}명의 사용자를 성공적으로 생성하였습니다."))
            