

library('tidyverse')

library("readxl")

library("ggplot2")

library('dplyr')

library('stringr')

library(data.table)

pop_df = read_excel('C:/Users/hanit/Desktop/dataton 2025/data/population 2022.xlsx')


age_sex_df <-   pop_df %>% filter(LocalityCode == 473) %>%  select(
                  'm_age0_4_pcnt',	'm_age5_9_pcnt',	'm_age10_14_pcnt',
                  'm_age15_19_pcnt',	'm_age20_24_pcnt',	'm_age25_29_pcnt',	'm_age30_34_pcnt',	
                  'm_age35_39_pcnt',	'm_age40_44_pcnt',	'm_age45_49_pcnt',	'm_age50_54_pcnt',	
                  'm_age55_59_pcnt',	'm_age60_64_pcnt',	'm_age65_69_pcnt',	'm_age70_74_pcnt',	
                  'm_age75_79_pcnt',	'm_age80_84_pcnt',	'm_age85_89_pcnt',	'm_age90_pcnt',
                  'w_age0_4_pcnt',	'w_age5_9_pcnt',	'w_age10_14_pcnt',	'w_age15_19_pcnt',	
                  'w_age20_24_pcnt',	'w_age25_29_pcnt',	'w_age30_34_pcnt',	'w_age35_39_pcnt',	
                  'w_age40_44_pcnt',	'w_age45_49_pcnt',	'w_age50_54_pcnt',	'w_age55_59_pcnt',	
                  'w_age60_64_pcnt',	'w_age65_69_pcnt',	'w_age70_74_pcnt',	'w_age75_79_pcnt',	
                  'w_age80_84_pcnt',	'w_age85_89_pcnt',	'w_age90_pcnt') 



# transpose
t_age_sex_df <- transpose(age_sex_df)

t_age_sex_df <-  t_age_sex_df %>% rename(percentage = V1)
t_age_sex_df$age = colnames(age_sex_df) 
t_age_sex_df$sex = str_split(t_age_sex_df$age, "_", simplify=TRUE)[,1]
t_age_sex_df$age = substring(t_age_sex_df$age,3,length(t_age_sex_df$age))


ggplot(t_age_sex_df) + 
  geom_col(data=subset(t_age_sex_df,sex=="m"),aes(x = percentage, y = age, fill = sex)) +
  geom_col(data=subset(t_age_sex_df,sex=="w"),aes(x = -percentage, y = age, fill = sex)) + 
  scale_x_continuous(breaks=seq(-5,5,0.5),labels=abs(seq(-5,5,0.5)))












