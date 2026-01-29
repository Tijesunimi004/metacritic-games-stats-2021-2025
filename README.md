# 🎮 Post-COVID Video Games Worldwide (2021-2025)

## 📌 Context
The gaming industry underwent a massive transformation following the global pandemic. This dataset captures the "Post-COVID" era of video games, covering titles released between **January 2021 and December 2025**. It tracks critical reception, user sentiment, and platform distribution during a period defined by the rise of next-gen consoles (PS5, Xbox Series X, Nintendo Switch 2) and shifting consumer habits.

## 📂 Content
This dataset contains **2,006** unique entries scraped from Metacritic. It includes data on game titles, platforms, release dates, and performance metrics (scores and review counts).

### **Columns & Data Dictionary**
| Column Name | Description | Data Type |
| :--- | :--- | :--- |
| **Title** | Name of the video game. | String |
| **Platform** | The console or operating system the game was released on (e.g., PS5, PC, Switch 2). | String |
| **Release_Date** | The official release date of the game (Range: 2021-01-07 to 2025-12-11). | Date |
| **Metascore** | The weighted average score from professional critics (0-100). | Integer |
| **User_Score** | The average score submitted by users (0-10). | Float |
| **Critic_Review_Count** | Total number of professional reviews used to calculate the Metascore. | Integer |
| **User_Review_Count** | Total number of user ratings submitted. | Integer |
| **Publisher** | The company that published the game (922 unique publishers). | String |
| **Genre** | The primary genre(s) of the game. | String |
| **Rating** | ESRB Age Rating (e.g., M, T, E, Not Rated). | String |
| **URL** | Direct link to the Metacritic page for the game. | String |

## 💡 Inspiration / Use Cases
This dataset is ideal for:
* **Sentiment Analysis:** Comparing `Metascore` (Critics) vs. `User_Score` (Gamers) to find controversial titles.
* **Trend Analysis:** How have game ratings changed from 2021 to 2025?
* **Platform Wars:** Which console had the highest-rated exclusives in the post-COVID era?
* **Publisher Performance:** Which publishers dominated the market in terms of volume and quality?

## 🛠️ Methodology
* **Source:** [Metacritic](https://www.metacritic.com)
* **Collection Date:** January 2026
* **Tools Used:** Python (BeautifulSoup/Selenium), Pandas.
