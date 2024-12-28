import torch
from sentence_transformers import SentenceTransformer, util
from groq import Groq

# Initialize SBERT model and Groq client
sbert_model = SentenceTransformer('all-mpnet-base-v2')  # Your chosen SBERT model
model = "llama-3.1-70b-versatile"
client = Groq(api_key="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")  # Replace with your actual Groq API key

def rag_with_sbert_and_llama(raw_text, questions, top_k=2):
    """
    Perform Retrieval-Augmented Generation (RAG) on a long raw text for a list of questions.

    Args:
        raw_text (str): The input text to process.
        questions (list): A list of questions to answer.
        top_k (int): Number of top relevant text chunks to retrieve.

    Returns:
        dict: A dictionary with questions as keys and generated answers as values.
    """
    # Step 1: Split the raw text into chunks
    chunks = raw_text.split('\n')  # Split by lines; you can use other methods to split large texts into smaller chunks
    
    # Step 2: Embed the chunks
    chunk_embeddings = sbert_model.encode(chunks, convert_to_tensor=True)
    
    def retrieve_documents(question, embeddings):
        """Retrieve the most relevant text chunks for a given question."""
        question_embedding = sbert_model.encode(question, convert_to_tensor=True)
        similarity_scores = util.pytorch_cos_sim(question_embedding, embeddings)[0]
        top_results = torch.topk(similarity_scores, k=top_k)
        top_indices = top_results.indices.cpu().numpy()
        return [(chunks[idx], similarity_scores[idx].item()) for idx in top_indices]
    
    def generate_answer(question, retrieved_chunks):
        """Generate an answer using Groq's LLaMA model based on retrieved chunks."""
        context = " ".join([chunk for chunk, _ in retrieved_chunks])
        system_query = (
            "You are a helpful assistant. Use the provided context to answer the user's query. "
            "If the context does not have enough information, respond with '---' and nothing else. "
            "Do not use information outside the context. Do not make up facts."
        )
        user_query = f"Context: {context}\nQuestion: {question}\nAnswer:"
        
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_query},
                {"role": "user", "content": user_query}
            ],
            model=model,
        )
        return chat_completion.choices[0].message.content.strip()
    
    # Step 3: Process each question
    answers = {}
    for question in questions:
        retrieved_chunks = retrieve_documents(question, chunk_embeddings)
        answer = generate_answer(question, retrieved_chunks)
        answers[question] = answer
        print("Question: ", question, "Answer: ", answer, "\n\n\n\n")
    
    return answers

# Example usage
raw_text = """
I try to consider myself a little bit in the middle of the road but when it comes down to judging where car brands are currently ranked I have opinions and I'm sharing them with you today we are going to be ranking the worst car brand loyalties that you can have so I'm Alex Alex I'm martini with two underscores on Instagram and today we're talking about cars okay I put the list of the the manufacturers that we do have ranked actually in the description pinned comment here which you can then change around and send it to me in the comments and tell me why you changed it around we start off with f the only brand that's F tier right now in my opinion is not Hyundai got your ass it's Tesla my problem with Tesla is that I think they're doing a great job in the EV space and I think they're doing a pretty good job kind of building their own thing but from a car manufacturer perspective they still got a long way to go the consumer appreciation or the consumer like what do you even call it most reliable cars by brand in 2018 2019 Tesla was ranked the 31st also the worst in the list by at 57.3 not only that but I do think sometimes to Tesla people do make me a little uncomfy okay I don't know what it is the constant need to tell me about the 0-60 time or just the fact that they all look like the one kid that wanted to tell you a fun fact in school but wasn't allowed to because the class ran out of time and then they kept you behind to tell you it anyway I'm just not a big fan but there's still an F going up into D in no particular order number one Jeep borderline F more expensive than it's worth it doesn't tell it's for some reason people are Cults to jeeps and I don't know why I don't know if if you go into a Jeep dealership if they stab you with like some sort of penicillin that makes you love the fact that everything below the ankles is terrible and analog and I get why I've gotten the Jeep Spiel from Jeep people oh it's so that water can get inside the Jeep no it's not Fiat is making those Jeeps as cheap as humanly possible and they've marketed your ass to believe that power seats aren't waterproof okay let me tell you for sixty thousand dollars you should get a couple things that can move when you press a button it blows my mind that you can't do that and don't get me wrong Jeep is kind of cool and the fact that the Jeep Wrangler Remains the best vehicle for holding its value I don't know what's holding up the value of these Jeeps the girls at UCLA I don't know if it's my wife I don't know if it's the men I don't know what's going on but I don't like it next Maserati pretty much only owned for masochist but I have never heard a single person in my entire life say I love maintaining my Maserati I love owning this card nope nobody I don't even I know two people that have one Maserati's sitting on the D list okay next up and I hate to do it to the brand I hate to do it Mitsubishi okay it's an air conditioning company that sometimes makes cars and I wanted to give it a better score okay practically SUVs with Wicked warranties at this point but Mitsubishi they don't have anything cool in the lineup anymore there's nothing exciting in the lineup I go to Mitsubishi I go to die my life is inherently over I have gotten the kids I have locked my career in and I am just stuck the only thing though okay and I want to be clear because we're jumping into the sea tier now the only thing that separates Mitsubishi from this next brand which might hurt some feelings is one car and that's the Miata because at the bottom of c-list is Mazda but for some reason the only thing they have left are SUVs and Mazda Miata which I would argue that they can barely make because they're still splitting differences with Fiat try and keep it moving and that worries me because the moment the Miata goes away Mazda is going to lose a lot of their fluff Fiat that's on the list too it's your art teacher in third grade fiat's cool they do stuff and things but for some reason every single time time I think a Fiat I think a Mini Cooper and when I think of Mini Cooper it's just like a more pronounced brand I don't mind Fiat the fiata bar 500 has to be one of my favorite little tiny Tinker cars that you could possibly drive but I've never seen them in enough of like a presence to say like that looks like a fun group to be a part of like Mazda at least has like RX-8 owners that just enjoy getting their kicked in constantly and they're like this is a blast I love it fdrx7 owners are like this is a blast I love it Fiat I just don't think really has that I had to come in with a little bit of domestic love because mid-tier C the first one of the big three is it's going to General Motors but it's going to Chevy specifically okay it's the drunk Perkins trip I tried to make these all analogies so that I could help maybe you can put your own Halo 2 intro statement on these but for me it's a drunk Perkins trip and let me explain why I've never out of my way have chosen to go to Perkins and I don't think you have either and I don't like it okay and Chevy feels a little bit the same way they've got the Corvette and the Malibu but somehow the Camaro is dead the Corvette Z06 super dope super exciting an absolute treat a blast a 2 30 a.m Perkins run with your boys and gals while you're having a good time a little bit drunk okay but once you sober up all you really realistically have in the lineup is a Malibu then we have Acura okay and there's two ways that I could explain this because there's some good cars in the lineup but for some reason when I look at Honda and Acura I don't think of Acura being above Honda I don't know what it is with that I don't know where I am if I'm in the wrong you will definitely correct me because you're the internet but Acura is not that fantastic for me when I compare it to Honda even with the release of the type S that they're planning to do I know that it's a re-badge slightly nicer Honda Civic Type R but the Honda Civic Type R is already a really nice car so I don't really know why I would buy an Acura when Type R exists anyway the analogy that I have for this one is have you ever taken a poop and thought you didn't need to wipe it then realize you do and now you're disappointed because you have to go back to the bathroom that's how I feel about Acura top of c-list is Mercedes-Benz it's like the League of Legends all chat I really enjoy Mercedes-Benz when I own them after their depreciation curve but if you buy anything from Mercedes that's like 2022 to 2017 that is a clean title that isn't an AMG GTC or GTR you are paying so much out the ass it doesn't financially make sense for you to be buying a Mercedes-Benz the cars are fantastic but the depreciation can put you in a coma b b is where things start to get hot a little bit heavy but still monetization appropriate because I need food Ford is like a Lisa's O'Hare that's all like they've got the Mustang they got the Bronco they got the Raptor they got the Ford Raptor Ranger they got a ton of SUVs but at least they still have some cool stuff in the lineup that's what I do like about Ford it seems like a more refined Dodge where it's like hey we're gonna give you some cool stuff but we're still going to make stuff that everybody wants to buy like the Ford F-150 is just like it's never going to stop being made it's made like every eight minutes but that's where it sits that's we're all in right next to it is Nissan Nissan's still doing good they're still supporting the S chassis they still have 10 years with a 350Z in 10 years with the 370Z so the support's gonna exist forever if the GTR is still a good car even though they keep making it forever and ever and ever it's a Nissan thing to do the only thing I have to say about it is that they need to pull through with the Nissan Z the Nissan Z has to hit its core audience because if it doesn't there is no sports car Option in the Nissan lineup outside of the GTR nobody can afford that why am I burping Dodge is up next you remember the meme where it's like yeah concrete that's Dodge nobody buying a Dodge Hellcat for the interior they're buying it so that they can just literally do the most basic childish man-child actions behind a steering wheel and it's still considered legal because Dodge does all of that for you you just press the pedal and go it's literally just a less tech savvy Tesla owner in my opinion and you still get the crazy ass drivers that come along with it I want one like secretly but I just don't think I'd ever actually buy one next up getting to the top of the list we've had between two left in the in the b list we got Audi which I would consider to be like Olive Garden when you went to prom in high school very fancy at the time you thought it was a very nice quality place they served Italian food so that meant that it was good and the brick looked cool but then as you get older you realize it's fake it's actually not that great and the prices aren't that insane so Audi as a whole that's what it is for me the performance models of Audi slap they're super good but it's still kind of a boring car it's a very standard clad design you're not going to get anything too excessive with Audi I would argue that even its most excessive designs like the R8 and the RS6 aren't that excessive when you look at the grandiose competition in the space now that may speak to people that love that and I would argue that once you get past one generation Audis make a great car there's a guy here in town his name's Cornelius he has oh I've seen him driving RS5 he had some RS models he had some other cars but this man always picks up like that that year RS like it's always one generation off and he makes them beautiful oh my God I want one top of the b list goes out to Lexus it's good Lexus has like this recent EV push that's pretty mediocre also Mazda's new CEO has a huge EV push Lexus also has this and they're still innovating they're just not innovating in the space people want they're they're innovating like yoke designs and drive-by wire designs in their EV SUVs that feel very very weird you can turn a Lexus steering wheel 90 degrees and get almost a full lock of steering in the new Lexus SUV that is nuts to me Tesla can't do that with a Tesla plan and they still introduce the Yoke design that you can't do the thing with it looks cool it looks like a rocket ship but once you start to drive it you're like where the is the top of my steering wheel at least Lexus has that going that's why it's a b Tesla was enough you know we're going into a territory now bottom of the list Volvo this is the suit you buy after your first wedding okay it's good a little pricey but you still appreciate it if you own one the pole Stars I think look fantastic you good quality fantastic cars are great the pole Stars I think are way too pricey but the pole star editions within the Volvo lineup look awesome I think that when you do pick one of these up if you're one of the few a lot of times if you can afford it you really are getting a bang on car that can do pretty much everything without it being too excessive in any regard do I have a hair in my eye or are you just happy to see me now we have Volkswagen Volkswagen's a good one it's a good restaurant you go to where the one waiter got in trouble in the local news for being racist because Volkswagen just always seems to get in trouble every like 10 years they do something just idiotic they get caught with their pants down but they make really good food sometimes you just gotta eat that's Volkswagen for me I've never actually personally owned a Volkswagen but there's a lot of people that have and they love them and it's like a cult and once you get in it man that is a plastic bag waffles oh he's just gonna lay in it perfect that's that's my favorite thing to do above Volkswagen though which might make a couple people upset it's BMW let me explain why BMW is up here okay because to me it's like if you had to go go to brunch with your significant others friends and you didn't want to but once you're there you really enjoy it that is BMW BMW's new G80 series all that sort of stuff their new M4 their new M3 the front end it took a bit for a lot of people to get used to the M2 competition the new one took a lot of time for people to get you know adjusted to that does not change the fact that these cars are fantastic it does not change the fact that BMW is on another goddamn level with their Interiors designing with what you get out of the box for the value sure they depreciate a little bit but oh my God these cars are lovely top of the A-list is Toyota my analogy for that one would be like Toyota's like Mommy you know Toyota's like if LeBron James didn't play basketball that's what Dakota told me to tell you but for me Toyota is just good it's it's got It's got the best appreciation opportunity across its entire lineup technically speaking from which cars to buy you should buy Toyotas are the only ones that go up in price next to our s tiered cars that we're about to talk about there's nothing in the Toyota lineup that doesn't meet some sort of demand from anyone in the the whole world and they do it really well and the new super in my opinion is probably one of the best sports cards you can buy s tier baby we're coming in with number three Suzuki okay the category you always go to in your incognito mode that is Suzuki Suzuki was the most reliable brand in 2018. the Suzuki still makes some incredible Vehicles out there and Suzuki's well known internationally first off Americans just because it doesn't do well into America land doesn't mean it doesn't do well period Suzukis are awesome they're affordable they do a lot of off-road cool they're small they're funky but they're not ugly I love them you should too Suzuki's are bang on thing they should come back to the United States in force and I would happily drive one if not I'm buying a k truck and no one can tell me otherwise second place was tied between two Brands Honda and Porsche it's not Porsche unless you own one second place to me unfortunately and I hate to say it it goes to Porsche now here's why Porsche is a supper club with four wheels they have everything going for them right now they the 911 is undoubtedly my favorite sports car it's one of the best sports cars ever made it has the Turbo S lineup it has the turbo it's got the 911 it's got all the different variants it's got the Targa it's got the GTS it's got everything okay they have something for the upper echelon of this scene and I don't mind it I want a Porsche I want to start buying budget Porsches building them then selling them and hopefully you get enough money to have a really expensive 911 one day because that is my my I want one so very bad but Porsche is expensive it's a little too much for me it's a little too much for pretty much anyone and the markups on them are insane and the dealers don't help so number one goes out to Honda it is the Tapatio of cars right now Honda is such a balanced platform for pretty much anyone for any type of Enthusiast they're Si's fantastic trim even the ex budget stuff when you start getting into it you go into old school stuff awesome cars the type R is a fantastic fantastic platform and I have not heard a single person that is jumping into a type bar that goes out and doesn't enjoy it and from a value per dollar perspective the Honda Civics can can't be beat they're reliable they're everywhere they last a long time you can get them serviced literally anywhere they're still a Honda they're affordable and they do a really good job so that my friends is my rankings of a through F on the car manufacturers of 2023 you let me know if you think I'm nuts or if you think I'm on to something I'm Alex Alex I'm martini with two underscores on Instagram and we will see you later adios [Music] finally [Music]
"""

questions = [
    "What is a brief overview of the diversity in the automotive industry and its significance for enthusiasts and newcomers?",
    "What criteria are used to evaluate and rank the top car brands in terms of history, model popularity, pricing, and innovation?",
    "What are the histories, notable models, and unique selling points of the top 5 car brands, including their average pricing?",
    "How do the top 5 car brands compare in terms of pricing, innovation, and technology advancements, and what are their respective strengths and weaknesses?",
    "Which car brand is ranked as the top brand and what are the reasons behind its ranking, including any exclusive features or achievements?",
    "What is a summary of the top 5 car brands, their unique contributions to the automotive world, and the criteria that make them stand out as the crème de la crème of the industry?"
]

answers = rag_with_sbert_and_llama(raw_text, questions)
# for question, answer in answers.items():
#     print(f"Q: {question}\nA: {answer}\n")