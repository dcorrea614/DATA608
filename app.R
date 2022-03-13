library(shiny)
library(bslib)
library(tidyverse)
library(plotly)

thematic::thematic_shiny()


df <- read_csv('https://raw.githubusercontent.com/charleyferrari/CUNY_DATA608/master/lecture3/data/cleaned-cdc-mortality-1999-2010-2.csv')

year_mortality_rate <- df %>%
  group_by(ICD.Chapter, Year) %>%
  summarise(nations_mortatlity_rate = sum(Deaths) / sum(Population)) %>%
  ungroup()
df <- df %>% left_join(year_mortality_rate, by=c("ICD.Chapter","Year"))
df_2010 <- df %>% filter(Year == 2010)
states = as.list(distinct(df, State))


# Define UI for application that draws a histogram
ui <- fluidPage(
    theme = bs_theme(version = 4, bootswatch = "superhero"),
   
    # Application title
    titlePanel(h1("DATA608 - Assignment 3")),
    
    h2("Question 1") ,
    p("As a researcher, you frequently compare mortality rates from particular causes across different States. You need a visualization that will let you see (for 2010 only) the crude mortality rate, across all States, from one cause (for example, Neoplasms, which are effectively cancers). Create a visualization that allows you to rank States by crude mortality for each cause of death.)"),
    h2("Question 2") ,
    p("Often you are asked whether particular States are improving their mortality rates (per cause) faster than, or slower than, the national average. Create a visualization that lets your clients see this for themselves for one cause of death at the time. Keep in mind that the national average should be weighted by the national population."),

    tabsetPanel(
      tabPanel("Question 1",
        sidebarLayout(
          sidebarPanel(
            
              selectInput("cod1",
                          "Cause of Death (Single Selection)",
                          distinct(df_2010, ICD.Chapter),
                          selected = "Neoplasms")),
          
          mainPanel(
            br(),
            plotlyOutput("rank")))
        ),
      
      tabPanel("Question 2",
        sidebarLayout(
            sidebarPanel(
              
              selectInput("cod2",
                          "Cause of Death (Single Selection)",
                          distinct(df_2010, ICD.Chapter),
                          selected = "Neoplasms"),
              
              selectInput("states",
                          "States (Multiple Selections)",
                          states,
                          selected = "NY",
                          multiple = TRUE)),

          mainPanel(
            br(),
            plotlyOutput("mort"))
))))


# Define server logic required to draw a histogram
server <- function(input, output) {
  
  tab1data <- reactive({
    df_2010 %>% 
      filter(ICD.Chapter == input$cod1) %>%
      select(ICD.Chapter, State, Crude.Rate)})
    
  tab2data <- reactive({
    df %>%
      filter(ICD.Chapter == input$cod2 & State %in% input$states) %>%
      mutate(mortality_rate = Deaths / Population) %>%
      select(ICD.Chapter, Year, State, mortality_rate, nations_mortatlity_rate) %>%
      gather(rate_type, rates, mortality_rate:nations_mortatlity_rate, factor_key = TRUE)
      })

  output$rank <- renderPlotly({

    fig <- plot_ly(tab1data(), 
            x = ~Crude.Rate, 
            y = ~reorder(State, Crude.Rate), 
            type = "bar", 
            orientation = "h",
            marker = list(color = 'rgb(222,45,38,0.8)'))
    
    fig %>%
      layout(
        xaxis = list(title = ""),
        yaxis = list(title = ""),
        title = "States by Crude Rate in 2010")%>%
      layout(plot_bgcolor="transparent") %>% 
      layout(paper_bgcolor="transparent") %>%
      layout(font = list(color="#FFFFFF"))
  })
  
  output$mort <- renderPlotly({
    
    fig <- plot_ly(tab2data(), 
                   x = ~Year, 
                   y = ~rates, 
                   type = "scatter", 
                   mode = "lines",
                   linetype = ~rate_type,
                   color = ~State)
    
    fig %>%
      layout(
        xaxis = list(title = ""),
        yaxis = list(title = ""),
        title = "Nation and State Mortality Rate") %>%
      layout(plot_bgcolor="transparent") %>% 
      layout(paper_bgcolor="transparent") %>%
      layout(font = list(color="#FFFFFF"))
    
  })
 
}

# Run the application 
shinyApp(ui = ui, server = server)
