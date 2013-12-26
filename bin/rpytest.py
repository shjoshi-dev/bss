import rpy2.robjects
f = file("/Volumes/Users/sjoshi/research/tools/stats/bst/bst/test/data/fears/anova_shape_R.R")
code = ''.join(f.readlines())
print code
print "\n"

result = rpy2.robjects.r(code)
X = rpy2.robjects.globalenv['result_data_table_one_func']
print X


# str1 = '''
# library(data.table)
# bipolar_demographics<-read.csv("bipolar_demographicsBAK.csv")
# source("read_attribute_matrix.R")
# df<-read_attribute_matrix()
# phenotype_array <- matrix(df$array, nrow = df$num_subjects, byrow = TRUE)
# phenotype_array <- t(phenotype_array)
# bipolar_demographics$sex<-factor(bipolar_demographics$sex)
# 
# anova_R <- function(formula_full, formula_null, unique_term) {
#   lm_full <- lm(formula_full)
#   lm_null <- lm(formula_null)
#   model_comparison = anova(lm_full, lm_null)
#   t_full = lm_full$coefficients[[unique_term]]
#   return (t_full/abs(t_full)*model_comparison[["Pr(>F)"]][2])
# }
# 
# ptm <- proc.time()
# phenotype_array_slice <- phenotype_array[,1001:2000]
# temp_df <- data.frame(bipolar_demographics$mri_id, as.data.frame(phenotype_array_slice))
# names(temp_df)[names(temp_df)=="bipolar_demographics.mri_id"] <- "mri_id"
# df_total <- merge(bipolar_demographics, temp_df, by="mri_id")
# '''
# str2 = '''
# dt_total <- data.table(df_total)
# temp<-dt_total[, list(variable = names(.SD), value = unlist(.SD, use.names = FALSE)), by = c("mri_id", "sex", "age", "height", "weight", "bp", "country")]
# 
# result_data_table_one_func <- temp[, as.list(anova_R(value ~ sex + age, value ~ sex , "age")), by=variable]
# print(proc.time() - ptm)
# '''
# 
# result = rpy2.robjects.r(str1)
# 
# result = rpy2.robjects.r(str2)
# X = rpy2.robjects.globalenv['result_data_table_one_func']
# print X
